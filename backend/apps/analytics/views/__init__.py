"""AI 分析视图"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services import AIAnalysisService
from apps.leads.models import Lead
from apps.leads.services import serialize_lead


class LeadAnalysisView(APIView):
    """单条线索分析：需求摘要 + 语义筛查 + 话术"""

    def get(self, request, pk):
        lead = Lead.objects.filter(id=pk, user=request.user).first()
        if not lead:
            return Response({"detail": "不存在"}, status=404)
        return Response({
            "result": {
                "lead": serialize_lead(lead),
                "summary": AIAnalysisService.summarize(lead),
                "sentiment": AIAnalysisService.sentiment_filter(lead),
                "script": AIAnalysisService.generate_script(lead),
            }
        })


class BatchRescreenView(APIView):
    """批量重筛"""

    def post(self, request):
        min_score = request.data.get("min_score")
        max_count = request.data.get("max_count")
        result = AIAnalysisService.rescreen(
            request.user,
            min_score=int(min_score) if min_score else None,
            max_count=int(max_count) if max_count else None,
        )
        return Response({"result": result})


class ScriptView(APIView):
    """话术生成（批量）"""

    def post(self, request):
        ids = request.data.get("ids", [])
        leads = Lead.objects.filter(id__in=ids, user=request.user)
        scripts = [{"id": lead.id, **AIAnalysisService.generate_script(lead)} for lead in leads]
        return Response({"results": scripts})
