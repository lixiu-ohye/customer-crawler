"""任务调度服务：线程执行采集管线 + 定时调度（Celery/进程内）"""
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from apps.crawler.services.auto_tagging import AutoTagging
from apps.crawler.services.crawler_service import CrawlerService
from apps.crawler.services.data_cleaner import DataCleaner
from apps.crawler.services.intent_scoring import IntentScoring
from apps.crawler.services.task_queue import TaskQueue
from apps.keywords.models import Keyword
from apps.keywords.services import KeywordService
from apps.leads.services import LeadService
from apps.tasks.models import CrawlTask

logger = logging.getLogger(__name__)

# 全局任务队列单例（进程内 + Redis）
TASK_QUEUE = TaskQueue(redis_url=settings.REDIS_URL)

# 平台显示名
PLATFORM_LABELS = {
    "douyin": "抖音", "xiaohongshu": "小红书", "kuaishou": "快手",
    "weibo": "微博", "zhihu": "知乎", "tieba": "贴吧",
}


class TaskService:
    """采集任务服务"""

    def __init__(self):
        self.crawler = CrawlerService(settings.CRAWLER_SETTINGS)
        self.scorer = IntentScoring(settings.INTENT_SCORING)

    def _sync_queue_task(self, task: CrawlTask, queue_task: dict):
        """将队列任务状态同步回 ORM"""
        task.status = queue_task["status"]
        task.progress = queue_task.get("progress", 0)
        task.total = queue_task.get("total", 0)
        task.processed = queue_task.get("processed", 0)
        task.found = queue_task.get("found", 0)
        task.message = queue_task.get("message", "")
        if queue_task.get("status") in ("completed", "failed", "stopped"):
            task.finished_at = timezone.now()
        task.save(update_fields=["status", "progress", "total", "processed", "found", "message", "finished_at"])

    def start(self, task: CrawlTask):
        """启动采集任务（异步线程）"""
        # 配额检查
        user = task.user
        if user.quota_used >= user.quota_limit:
            task.status = "failed"
            task.message = "采集配额已用尽，请升级套餐"
            task.save()
            return task

        keywords = [k.strip() for k in task.keywords.split(",") if k.strip()]
        platforms = task.platforms or []
        pages = task.pages or 1

        # 预取关键词（含否定词）
        db_keywords = list(Keyword.objects.filter(user=user, word__in=keywords))
        negative_words = KeywordService.extract_negative_keywords(db_keywords)
        kw_words = [k.word for k in db_keywords] or keywords

        def pipeline(*, task_id, stop_flag, **_):
            queue_task = TASK_QUEUE.get_task(task_id) or {}
            total_units = len(keywords) * len(platforms) * pages
            queue_task["total"] = total_units
            TASK_QUEUE.update_progress(task_id, total=total_units, message="开始采集...")

            processed = 0
            found_total = 0
            for kw in keywords:
                for platform in platforms:
                    if stop_flag.is_set():
                        TASK_QUEUE.set_status(task_id, "stopped", "用户已停止")
                        return
                    label = PLATFORM_LABELS.get(platform, platform)
                    TASK_QUEUE.update_progress(
                        task_id, message=f"正在采集：{label} / {kw}",
                    )
                    try:
                        items = self.crawler.crawl_keyword(platform, kw, pages=pages)
                    except Exception as exc:
                        logger.exception("crawl error %s/%s", platform, kw)
                        items = []
                    # 清洗
                    items = DataCleaner.process_batch(items)
                    # 打分 + 标签
                    for item in items:
                        item["intent_score"], _ = self.scorer.score(item, kw_words, negative_words)
                        item["tags"] = AutoTagging.generate(item, item["intent_score"])
                    # 入库
                    created = LeadService.create_from_items(user, items, task_id=str(task.id))
                    found_total += created
                    processed += len(items)
                    TASK_QUEUE.update_progress(
                        task_id, processed=processed, found=found_total,
                        message=f"{label}「{kw}」完成，新增 {created} 条线索",
                    )
                    if stop_flag.is_set():
                        TASK_QUEUE.set_status(task_id, "stopped", "用户已停止")
                        return
            TASK_QUEUE.update_progress(task_id, processed=processed, found=found_total, progress=100)
            TASK_QUEUE.set_status(task_id, "completed", f"采集完成，共新增 {found_total} 条线索")

        queue_task = TASK_QUEUE.create_task(
            id=f"task_{task.id}", status="pending", total=1,
            message="任务已创建，等待启动",
        )
        task.status = "running"
        task.save()
        TASK_QUEUE.run_async(queue_task["id"], pipeline)
        return task

    def stop(self, task: CrawlTask):
        TASK_QUEUE.stop(f"task_{task.id}")

    def pause(self, task: CrawlTask):
        ok = TASK_QUEUE.pause(f"task_{task.id}")
        if ok:
            task.status = "paused"
            task.save()

    def resume(self, task: CrawlTask):
        ok = TASK_QUEUE.resume(f"task_{task.id}")
        if ok:
            task.status = "running"
            task.save()

    def sync_status(self, task: CrawlTask):
        """把队列最新状态同步回 ORM（供轮询接口使用）"""
        queue_task = TASK_QUEUE.get_task(f"task_{task.id}")
        if queue_task:
            self._sync_queue_task(task, queue_task)

    # ---------- 定时调度 ----------
    def schedule_tasks(self):
        """按 cron 分钟字段检查到期任务并触发（由 scheduler 循环调用）"""
        now = timezone.now()
        due = CrawlTask.objects.filter(
            schedule_type__in=("minutely", "hourly", "daily", "weekly", "cron"),
            status__in=("pending", "completed", "failed", "stopped"),
            next_run_at__lte=now,
        )
        for task in due:
            self.start(task)
            self._compute_next_run(task)
            task.save()

    def _compute_next_run(self, task: CrawlTask):
        now = timezone.now()
        if task.schedule_type == "minutely":
            task.next_run_at = now + timedelta(minutes=1)
        elif task.schedule_type == "hourly":
            task.next_run_at = now + timedelta(hours=1)
        elif task.schedule_type == "daily":
            task.next_run_at = now + timedelta(days=1)
        elif task.schedule_type == "weekly":
            task.next_run_at = now + timedelta(weeks=1)
        else:
            # 简化 cron：仅支持分钟级触发
            task.next_run_at = now + timedelta(minutes=1)


task_service = TaskService()
