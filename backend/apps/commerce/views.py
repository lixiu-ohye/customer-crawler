"""商业化模块视图（最小可用版，后续扩展）"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.commerce.models import PlanDefinition, RealNameAuth, UserQuota, DeviceIpControl, UserBehaviorLog, ServicePurchase, Coupon, UserCoupon


class PlanDefinitionListView(APIView):
    """套餐定义列表"""

    def get(self, request):
        qs = PlanDefinition.objects.all()[:100]
        return Response({
            "results": [
                {"id": p.id, "name": getattr(p, "name", ""), "price": str(getattr(p, "price", 0)),
                 "duration_days": getattr(p, "duration_days", 0), "enabled": getattr(p, "enabled", True)}
                for p in qs
            ],
            "total": PlanDefinition.objects.count(),
        })


class ServicePurchaseListView(APIView):
    """服务购买记录"""

    def get(self, request):
        qs = ServicePurchase.objects.all()[:100]
        return Response({
            "results": [
                {"id": s.id, "user": getattr(s, "user", ""), "plan": getattr(s, "plan", ""),
                 "status": getattr(s, "status", ""), "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(s, "created_at", None) else ""}
                for s in qs
            ],
            "total": ServicePurchase.objects.count(),
        })


class UserQuotaListView(APIView):
    """用户配额列表"""

    def get(self, request):
        qs = UserQuota.objects.all()[:100]
        return Response({
            "results": [
                {"id": q.id, "user": getattr(q, "user", ""), "leads_quota": getattr(q, "leads_quota", 0),
                 "used": getattr(q, "used", 0)}
                for q in qs
            ],
            "total": UserQuota.objects.count(),
        })
