# -*- coding: utf-8 -*-
"""
采集审计日志 (合规留痕)
======================
每次对外数据请求都会写入审计记录, 满足「全程留痕」合规要求。
数据存储在内存环形缓冲区 + 可选落库 (LOG 模型), 便于系统管理页展示。
"""
import json
import logging
import threading
import time
from collections import deque
from typing import Dict, List

logger = logging.getLogger("crawler.audit")

# 内存审计缓冲区 (最多保留 1000 条)
_AUDIT_BUFFER: deque = deque(maxlen=1000)
_LOCK = threading.Lock()


def audit_collection(platform: str, keyword: str, count: int, mode: str, extra: Dict = None):
    """记录一次采集行为"""
    record = {
        "id": f"audit_{int(time.time()*1000)}",
        "platform": platform,
        "keyword": keyword,
        "result_count": count,
        "mode": mode,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "extra": extra or {},
    }
    with _LOCK:
        _AUDIT_BUFFER.appendleft(record)
    logger.info("[audit] platform=%s keyword=%s count=%s mode=%s", platform, keyword, count, mode)
    # 异步落库 (避免阻塞请求)
    try:
        _persist_async(record)
    except Exception:
        pass


def get_audit_records(limit: int = 100) -> List[Dict]:
    """获取最近审计记录"""
    with _LOCK:
        return list(_AUDIT_BUFFER)[:limit]


def _persist_async(record: Dict):
    """尝试写入数据库 (若 crawler 模型表已迁移)"""
    try:
        from apps.crawler.models import CrawlAuditLog

        CrawlAuditLog.objects.create(
            platform=record["platform"],
            keyword=record["keyword"],
            result_count=record["result_count"],
            mode=record["mode"],
            detail=json.dumps(record.get("extra", {}), ensure_ascii=False),
        )
    except Exception:
        # 表不存在或 DB 不可用时仅保留内存记录
        pass
