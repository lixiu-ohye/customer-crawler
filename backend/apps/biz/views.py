"""企业信息模块视图（最小可用版，后续扩展）"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.biz.models import Company, CompanyEvent, Contact, ScreenTemplate


class CompanyListView(APIView):
    """企业列表"""

    def get(self, request):
        qs = Company.objects.all()[:100]
        return Response({
            "results": [
                {"id": c.id, "name": c.name, "industry": getattr(c, "industry", ""),
                 "region": getattr(c, "region", ""), "contact": getattr(c, "contact", ""),
                 "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(c, "created_at", None) else ""}
                for c in qs
            ],
            "total": Company.objects.count(),
        })


class CompanyEventListView(APIView):
    """企业动态列表"""

    def get(self, request):
        qs = CompanyEvent.objects.all()[:100]
        return Response({
            "results": [
                {"id": e.id, "company_id": e.company_id, "title": getattr(e, "title", ""),
                 "content": getattr(e, "content", ""), "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(e, "created_at", None) else ""}
                for e in qs
            ],
            "total": CompanyEvent.objects.count(),
        })


class ContactListView(APIView):
    """联系人列表"""

    def get(self, request):
        qs = Contact.objects.all()[:100]
        return Response({
            "results": [
                {"id": c.id, "name": c.name, "company_id": c.company_id,
                 "phone": getattr(c, "phone", ""), "title": getattr(c, "title", "")}
                for c in qs
            ],
            "total": Contact.objects.count(),
        })


class ScreenTemplateListView(APIView):
    """筛选模板列表"""

    def get(self, request):
        qs = ScreenTemplate.objects.all()[:100]
        return Response({
            "results": [
                {"id": t.id, "name": t.name, "conditions": getattr(t, "conditions", ""),
                 "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(t, "created_at", None) else ""}
                for t in qs
            ],
            "total": ScreenTemplate.objects.count(),
        })
