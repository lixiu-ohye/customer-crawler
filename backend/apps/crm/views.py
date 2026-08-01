"""客户管理模块视图（最小可用版，后续扩展）"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crm.models import LeadPool, ExportAuditLog


class LeadPoolListView(APIView):
    """线索池列表"""

    def get(self, request):
        qs = LeadPool.objects.all()[:100]
        return Response({
            "results": [
                {"id": l.id, "name": getattr(l, "name", ""), "source": getattr(l, "source", ""),
                 "status": getattr(l, "status", ""), "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(l, "created_at", None) else ""}
                for l in qs
            ],
            "total": LeadPool.objects.count(),
        })


class ExportAuditLogListView(APIView):
    """导出审计日志列表"""

    def get(self, request):
        qs = ExportAuditLog.objects.all()[:100]
        return Response({
            "results": [
                {"id": e.id, "user": getattr(e, "user", ""), "action": getattr(e, "action", ""),
                 "detail": getattr(e, "detail", ""), "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(e, "created_at", None) else ""}
                for e in qs
            ],
            "total": ExportAuditLog.objects.count(),
        })
