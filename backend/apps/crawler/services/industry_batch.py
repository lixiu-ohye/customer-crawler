# -*- coding: utf-8 -*-
"""行业关键词批量自动采集服务
从 12 行业词库取关键词 → 批量启动 MediaCrawler 爬虫任务 → 任务完成后自动导入线索库
"""
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

from django.contrib.auth import get_user_model

from apps.keywords.industry_library import INDUSTRY_LIBRARY, all_words, all_negative_words
from apps.crawler.integrations.mediacrawler_adapter import (
    MediaCrawlerAdapter,
    TASK_STATUS,
)

logger = logging.getLogger(__name__)

# 批量采集任务存储（内存，生产用 Redis/DB）
BATCH_TASKS = {}
_BATCH_LOCK = threading.Lock()


class IndustryBatchTask:
    """行业批量采集任务"""

    def __init__(self, batch_id, industry, platforms, max_keywords=8, user_id=None):
        self.batch_id = batch_id
        self.industry = industry
        self.platforms = platforms
        self.max_keywords = max_keywords
        self.user_id = user_id
        self.status = "pending"  # pending/running/completed/failed
        self.created_at = datetime.now()
        self.finished_at = None
        self.keywords = []
        self.sub_tasks = []  # [{keyword, platform, task_id, status, result_count, import_result, error}]
        self.total_keywords = 0
        self.completed_keywords = 0
        self.imported_count = 0

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "industry": self.industry,
            "platforms": self.platforms,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": self.finished_at.strftime("%Y-%m-%d %H:%M:%S") if self.finished_at else None,
            "total_keywords": self.total_keywords,
            "completed_keywords": self.completed_keywords,
            "imported_count": self.imported_count,
            "sub_tasks": self.sub_tasks,
        }


def _run_batch_worker(batch_id):
    """后台执行批量采集：逐关键词启动爬虫（串行，避免多实例冲突）"""
    with _BATCH_LOCK:
        batch = BATCH_TASKS.get(batch_id)
    if not batch:
        return

    User = get_user_model()
    admin = None
    if batch.user_id:
        admin = User.objects.filter(id=batch.user_id).first()
    if not admin:
        admin = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_active=True).first()

    batch.status = "running"

    for item in batch.sub_tasks:
        if item["status"] != "pending":
            continue
        item["status"] = "running"
        try:
            # 启动单个关键词爬虫
            result = MediaCrawlerAdapter.create_task(item["platform"], item["keyword"], "search")
            task_id = result.task_id
            start_result = MediaCrawlerAdapter.start_task(task_id)
            item["task_id"] = task_id
            if not start_result.get("success"):
                item["status"] = "failed"
                item["error"] = start_result.get("error", "start failed")
                batch.completed_keywords += 1
                continue

            # 等待任务完成（轮询，单任务最长 5 分钟）
            deadline = time.time() + 300
            while time.time() < deadline:
                task = MediaCrawlerAdapter.get_task(task_id)
                if task and task.status in (TASK_STATUS["COMPLETED"], TASK_STATUS["FAILED"], TASK_STATUS["CANCELLED"]):
                    break
                time.sleep(3)

            task = MediaCrawlerAdapter.get_task(task_id)
            if task:
                item["result_count"] = task.result_count
                item["import_result"] = getattr(task, "import_result", 0)
                if task.status == TASK_STATUS["COMPLETED"]:
                    item["status"] = "completed"
                    batch.imported_count += (getattr(task, "import_result", 0) or 0)
                else:
                    item["status"] = "failed"
                    item["error"] = task.error_message or "unknown"
            else:
                item["status"] = "failed"
                item["error"] = "task lost"

        except Exception as e:
            item["status"] = "failed"
            item["error"] = str(e)
        finally:
            batch.completed_keywords += 1

        # 串行间隔（避免并发冲突 + 反爬）
        time.sleep(2)

    batch.status = "completed"
    batch.finished_at = datetime.now()


def start_industry_batch(industry, platforms, max_keywords=8, user_id=None):
    """启动行业批量采集

    Args:
        industry: 行业名（INDUSTRY_LIBRARY 键）
        platforms: 平台列表（weibo/douyin/xiaohongshu/kuaishou/zhihu/tieba）
        max_keywords: 每行业最多取关键词数
        user_id: 线索归属用户
    Returns:
        dict: {success, batch_id, industry, keywords, platforms}
    """
    if industry not in INDUSTRY_LIBRARY:
        return {"success": False, "error": f"未知行业: {industry}", "industries": list(INDUSTRY_LIBRARY.keys())}

    if not platforms:
        platforms = ["weibo"]

    # 取关键词：主词优先 + 长尾词补充，过滤否定词
    words = all_words(industry)
    negs = all_negative_words(industry)

    def _is_neg(w):
        for n in negs:
            if n and n in w:
                return True
        return False

    keywords = [w for w in words if not _is_neg(w)][:max_keywords]
    if not keywords:
        keywords = words[:1]  # 至少一个

    batch_id = "B" + datetime.now().strftime("%H%M%S") + str(len(BATCH_TASKS) % 97)

    batch = IndustryBatchTask(batch_id, industry, platforms, max_keywords=max_keywords, user_id=user_id)
    batch.keywords = keywords
    batch.total_keywords = len(keywords)
    for p in platforms:
        for kw in keywords:
            batch.sub_tasks.append({
                "keyword": kw,
                "platform": p,
                "task_id": None,
                "status": "pending",
                "result_count": 0,
                "import_result": 0,
                "error": None,
            })

    with _BATCH_LOCK:
        BATCH_TASKS[batch_id] = batch

    # 后台执行
    t = threading.Thread(target=_run_batch_worker, args=(batch_id,), daemon=True)
    t.start()

    return {
        "success": True,
        "batch_id": batch_id,
        "industry": industry,
        "platforms": platforms,
        "keywords": keywords,
        "sub_task_count": len(batch.sub_tasks),
        "message": f"已启动行业[{industry}]批量采集，{len(keywords)} 个关键词 × {len(platforms)} 平台",
    }


def get_batch(batch_id):
    """查询批量任务状态"""
    with _BATCH_LOCK:
        batch = BATCH_TASKS.get(batch_id)
    if not batch:
        return {"success": False, "error": "batch not found"}
    return {"success": True, "batch": batch.to_dict()}


def list_batches():
    """列出所有批量任务（新→旧）"""
    with _BATCH_LOCK:
        batches = [b.to_dict() for b in BATCH_TASKS.values()]
    return {"success": True, "batches": sorted(batches, key=lambda x: x["created_at"], reverse=True)}
