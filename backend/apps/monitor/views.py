"""舆情监控模块视图（最小可用版，后续扩展）"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitor.models import MonitorTarget, RawComment, IntentComment, TriggerRule, DmTemplate, AccountPool


class MonitorTargetListView(APIView):
    """监控目标列表"""

    def get(self, request):
        qs = MonitorTarget.objects.all()[:100]
        return Response({
            "results": [
                {"id": t.id, "name": getattr(t, "name", ""), "platform": getattr(t, "platform", ""),
                 "keyword": getattr(t, "keyword", ""), "status": getattr(t, "status", ""),
                 "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(t, "created_at", None) else ""}
                for t in qs
            ],
            "total": MonitorTarget.objects.count(),
        })


class IntentCommentListView(APIView):
    """意向评论列表"""

    def get(self, request):
        qs = IntentComment.objects.all()[:100]
        return Response({
            "results": [
                {"id": c.id, "content": getattr(c, "content", ""), "intent_score": getattr(c, "intent_score", 0),
                 "platform": getattr(c, "platform", ""), "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(c, "created_at", None) else ""}
                for c in qs
            ],
            "total": IntentComment.objects.count(),
        })


class TriggerRuleListView(APIView):
    """触发规则列表"""

    def get(self, request):
        qs = TriggerRule.objects.all()[:100]
        return Response({
            "results": [
                {"id": r.id, "name": getattr(r, "name", ""), "condition": getattr(r, "condition", ""),
                 "action": getattr(r, "action", ""), "enabled": getattr(r, "enabled", True)}
                for r in qs
            ],
            "total": TriggerRule.objects.count(),
        })
