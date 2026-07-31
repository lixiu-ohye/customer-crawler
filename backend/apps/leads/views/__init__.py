"""线索视图"""
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.leads.models import Lead
from apps.leads.services import LeadService, serialize_lead


class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LeadListView(APIView):
    """线索列表 / 筛选 / 分页"""

    def get(self, request):
        qs = LeadService.filter_queryset(request.user, request.query_params)
        paginator = LeadPagination()
        page = paginator.paginate_queryset(qs, request)
        data = [serialize_lead(lead) for lead in page]
        return Response({
            "results": data,
            "total": qs.count(),
            "page": paginator.page.number if paginator.page else 1,
            "pages": paginator.page.paginator.num_pages if paginator.page else 0,
        })


class LeadDetailView(APIView):
    """线索详情 / 备注 / 拉黑 / 收藏"""

    def _get(self, request, pk):
        return Lead.objects.filter(id=pk, user=request.user).first()

    def get(self, request, pk):
        lead = self._get(request, pk)
        if not lead:
            return Response({"detail": "不存在"}, status=404)
        return Response({"result": serialize_lead(lead)})

    def put(self, request, pk):
        lead = self._get(request, pk)
        if not lead:
            return Response({"detail": "不存在"}, status=404)
        if "note" in request.data:
            lead.note = request.data["note"]
        if "status" in request.data:
            lead.status = request.data["status"]
        if "is_favorite" in request.data:
            lead.is_favorite = bool(request.data["is_favorite"])
        if "is_blacklisted" in request.data:
            lead.is_blacklisted = bool(request.data["is_blacklisted"])
        lead.save()
        return Response({"result": serialize_lead(lead)})

    def delete(self, request, pk):
        lead = self._get(request, pk)
        if not lead:
            return Response({"detail": "不存在"}, status=404)
        lead.delete()
        return Response({"detail": "已删除"})


class LeadExportView(APIView):
    """导出 csv / xlsx"""

    def get(self, request):
        fmt = request.query_params.get("format", "csv")
        if fmt == "xlsx":
            data = LeadService.export_xlsx(request.user, request.query_params)
            resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            resp["Content-Disposition"] = 'attachment; filename="leads.xlsx"'
            return resp
        data = LeadService.export_csv(request.user, request.query_params)
        resp = HttpResponse(data, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="leads.csv"'
        return resp


class LeadBatchView(APIView):
    """批量操作：收藏 / 拉黑 / 删除 / 更新备注"""

    def post(self, request):
        action = request.data.get("action")
        ids = request.data.get("ids", [])
        leads = Lead.objects.filter(id__in=ids, user=request.user)
        if action == "favorite":
            leads.update(is_favorite=True)
        elif action == "unfavorite":
            leads.update(is_favorite=False)
        elif action == "blacklist":
            leads.update(is_blacklisted=True)
        elif action == "unblacklist":
            leads.update(is_blacklisted=False)
        elif action == "delete":
            leads.delete()
        elif action == "note":
            leads.update(note=request.data.get("note", ""))
        else:
            return Response({"detail": "未知操作"}, status=400)
        return Response({"detail": "操作成功", "count": leads.count()})
