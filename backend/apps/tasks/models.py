"""采集任务模型"""
from django.conf import settings
from django.db import models


class CrawlTask(models.Model):
    """采集任务"""

    STATUS_CHOICES = (
        ("pending", "待执行"), ("running", "执行中"), ("paused", "已暂停"),
        ("completed", "已完成"), ("failed", "失败"), ("stopped", "已停止"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crawl_tasks")
    name = models.CharField("任务名", max_length=128, blank=True, default="")
    keywords = models.TextField("关键词（逗号分隔）")
    platforms = models.JSONField("目标平台", default=list)
    pages = models.IntegerField("采集页数", default=1)
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="pending")
    progress = models.IntegerField("进度", default=0)
    total = models.IntegerField("总量", default=0)
    processed = models.IntegerField("已处理", default=0)
    found = models.IntegerField("发现线索", default=0)
    message = models.TextField("消息", blank=True, default="")
    schedule_type = models.CharField("调度类型", max_length=16, blank=True, default="")
    schedule_cron = models.CharField("Cron 表达式", max_length=64, blank=True, default="")
    last_run_at = models.DateTimeField("上次运行", null=True, blank=True)
    next_run_at = models.DateTimeField("下次运行", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    finished_at = models.DateTimeField("结束时间", null=True, blank=True)

    class Meta:
        db_table = "crawl_task"
        verbose_name = "采集任务"
        verbose_name_plural = verbose_name
        ordering = ("-id",)


def serialize_task(task):
    return {
        "id": task.id,
        "name": task.name,
        "keywords": task.keywords,
        "platforms": task.platforms,
        "pages": task.pages,
        "status": task.status,
        "progress": task.progress,
        "total": task.total,
        "processed": task.processed,
        "found": task.found,
        "message": task.message,
        "schedule_type": task.schedule_type,
        "schedule_cron": task.schedule_cron,
        "last_run_at": task.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if task.last_run_at else "",
        "next_run_at": task.next_run_at.strftime("%Y-%m-%d %H:%M:%S") if task.next_run_at else "",
        "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else "",
        "finished_at": task.finished_at.strftime("%Y-%m-%d %H:%M:%S") if task.finished_at else "",
    }
