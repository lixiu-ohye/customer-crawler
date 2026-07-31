"""数据统计服务：仪表盘、平台/意向/任务状态分布、趋势、热力图、关键词效果"""
from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone

from apps.leads.models import Lead
from apps.tasks.models import CrawlTask

PLATFORM_LABELS = {
    "douyin": "抖音", "xiaohongshu": "小红书", "kuaishou": "快手",
    "weibo": "微博", "zhihu": "知乎", "tieba": "贴吧",
}
INTENT_LABELS = {"high": "高意向", "medium": "中意向", "low": "低意向", "none": "无意向"}


class StatisticsService:
    """统计聚合"""

    @staticmethod
    def dashboard(user):
        leads = Lead.objects.filter(user=user)
        tasks = CrawlTask.objects.filter(user=user)
        total_leads = leads.count()
        high_intent = leads.filter(intent_label="high").count()
        avg_score = leads.aggregate(avg=Avg("intent_score"))["avg"] or 0
        running_tasks = tasks.filter(status="running").count()
        return {
            "total_leads": total_leads,
            "high_intent_leads": high_intent,
            "avg_intent_score": round(avg_score, 1),
            "running_tasks": running_tasks,
            "total_tasks": tasks.count(),
            "platforms_covered": len(PLATFORM_LABELS),
        }

    @staticmethod
    def platform_distribution(user):
        rows = Lead.objects.filter(user=user).values("platform").annotate(count=Count("id"))
        return [{"name": PLATFORM_LABELS.get(r["platform"], r["platform"]), "value": r["count"]} for r in rows]

    @staticmethod
    def intent_distribution(user):
        rows = Lead.objects.filter(user=user).values("intent_label").annotate(count=Count("id"))
        return [{"name": INTENT_LABELS.get(r["intent_label"], r["intent_label"]), "value": r["count"]} for r in rows]

    @staticmethod
    def task_status_distribution(user):
        rows = CrawlTask.objects.filter(user=user).values("status").annotate(count=Count("id"))
        status_map = dict(CrawlTask.STATUS_CHOICES)
        return [{"name": status_map.get(r["status"], r["status"]), "value": r["count"]} for r in rows]

    @staticmethod
    def trend(user, days=7):
        """近 N 天新增线索趋势"""
        since = timezone.now() - timedelta(days=days)
        leads = Lead.objects.filter(user=user, created_at__gte=since)
        buckets = {}
        for i in range(days):
            day = (timezone.now() - timedelta(days=days - 1 - i)).strftime("%m-%d")
            buckets[day] = 0
        for lead in leads:
            key = lead.created_at.strftime("%m-%d")
            if key in buckets:
                buckets[key] += 1
        return [{"date": k, "value": v} for k, v in buckets.items()]

    @staticmethod
    def heatmap(user):
        """地图热力图点位（按经纬度聚合，返回城市级点位）"""
        leads = Lead.objects.filter(user=user).exclude(lng__isnull=True).exclude(lat__isnull=True)
        points = {}
        for lead in leads[:2000]:
            key = (round(lead.lng, 2), round(lead.lat, 2))
            city = lead.region or ""
            if key not in points:
                points[key] = {"lng": key[0], "lat": key[1], "count": 0, "city": city}
            points[key]["count"] += 1
        return list(points.values())

    @staticmethod
    def keyword_effect(user):
        """关键词效果统计（按需求标签聚合）"""
        rows = Lead.objects.filter(user=user).values("demand").annotate(
            count=Count("id"), avg_score=Avg("intent_score")
        )
        return [
            {"name": r["demand"], "count": r["count"], "avg_score": round(r["avg_score"] or 0, 1)}
            for r in rows if r["demand"]
        ]
