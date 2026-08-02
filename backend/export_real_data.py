# -*- coding: utf-8 -*-
"""导出数据库真实数据为前端可用的 real-data.json"""
import os, sys, json
sys.path.insert(0, r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["PYTHONIOENCODING"] = "utf-8"
import django
django.setup()

from django.apps import apps
from django.db.models import Count

Lead = apps.get_model("leads", "Lead")
Keyword = apps.get_model("keywords", "Keyword")
Task = apps.get_model("tasks", "CrawlTask")

def lead_to_dict(l):
    return {
        "id": l.id,
        "platform": l.platform or "",
        "item_id": l.item_id or "",
        "title": l.title or "",
        "content": l.content or "",
        "author": l.author or "",
        "author_id": l.author_id or "",
        "url": l.url or "",
        "region": l.region or "",
        "demand": l.demand or "",
        "intent_score": l.intent_score or 0,
        "intent_label": l.intent_label or "low",
        "score_breakdown": l.score_breakdown or {},
        "tags": l.tags or [],
        "like_count": l.like_count or 0,
        "comment_count": l.comment_count or 0,
        "share_count": l.share_count or 0,
        "publish_time": l.publish_time.strftime("%Y-%m-%d %H:%M:%S") if l.publish_time else "",
        "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "",
        "status": l.status or "new",
        "note": l.note or "",
        "is_favorite": l.is_favorite,
        "is_blacklisted": l.is_blacklisted,
        "location_text": l.location_text or "",
    }

leads = [lead_to_dict(l) for l in Lead.objects.all().order_by("-intent_score", "-id")]
print(f"leads: {len(leads)}")

keywords = [{
    "id": k.id,
    "word": k.word,
    "group": k.group_id if hasattr(k, "group_id") else None,
    "group_name": getattr(k, "group_name", "") or "",
    "negative_words": getattr(k, "negative_words", "") or "",
    "hit_count": getattr(k, "hit_count", 0) or 0,
    "created_at": k.created_at.strftime("%Y-%m-%d %H:%M:%S") if k.created_at else "",
} for k in Keyword.objects.all()]
print(f"keywords: {len(keywords)}")

tasks = [{
    "id": t.id,
    "name": getattr(t, "name", "") or "",
    "keywords": getattr(t, "keywords", "") or "",
    "platforms": getattr(t, "platforms", []) or [],
    "status": getattr(t, "status", "") or "",
    "progress": getattr(t, "progress", 0) or 0,
    "message": getattr(t, "message", "") or "",
    "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(t, "created_at", None) else "",
} for t in Task.objects.all()]
print(f"tasks: {len(tasks)}")

# 平台分布（与 /stats/distribution 一致）
plat = Lead.objects.values("platform").annotate(c=Count("id"))
platform_names = {"weibo": "微博", "douyin": "抖音", "xiaohongshu": "小红书",
                  "kuaishou": "快手", "zhihu": "知乎", "tieba": "贴吧"}
platform_dist = [{"name": platform_names.get(p["platform"], p["platform"]), "value": p["c"]} for p in plat]

# 意向分布
high = Lead.objects.filter(intent_label="high").count()
medium = Lead.objects.filter(intent_label="medium").count()
low = Lead.objects.filter(intent_label="low").count()
none = Lead.objects.exclude(intent_label__in=["high", "medium", "low"]).count()
intent_dist = [{"name": "高意向", "value": high}, {"name": "中意向", "value": medium},
               {"name": "低意向", "value": low}]
if none:
    intent_dist.append({"name": "无意向", "value": none})

# 地域分布（heatmap）
from django.db.models import Count as C2
regions = Lead.objects.exclude(region="").exclude(region__isnull=True).values("region").annotate(c=C2("id")).order_by("-c")[:30]
region_dist = [{"name": r["region"], "value": r["c"]} for r in regions]

# 近 7 日趋势（按 created_at 日期聚合）
from django.utils import timezone
from datetime import timedelta
trend = []
now = timezone.now()
for i in range(6, -1, -1):
    day = now - timedelta(days=i)
    n = Lead.objects.filter(created_at__date=day.date()).count()
    trend.append({"date": day.strftime("%m-%d"), "value": n})

data = {
    "exported_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    "leads": leads,
    "keywords": keywords,
    "tasks": tasks,
    "platform_distribution": platform_dist,
    "intent_distribution": intent_dist,
    "region_distribution": region_dist,
    "trend": trend,
}

out = r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\frontend\src\api\real-data.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print(f"导出完成: {out} ({os.path.getsize(out)/1024:.1f} KB)")
