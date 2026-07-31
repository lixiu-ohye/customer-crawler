"""统计视图"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stats.services import StatisticsService


class DashboardView(APIView):
    def get(self, request):
        return Response({"result": StatisticsService.dashboard(request.user)})


class DistributionView(APIView):
    """分布：platform / intent / task_status"""

    def get(self, request):
        kind = request.query_params.get("kind", "platform")
        service = StatisticsService
        if kind == "intent":
            data = service.intent_distribution(request.user)
        elif kind == "task_status":
            data = service.task_status_distribution(request.user)
        else:
            data = service.platform_distribution(request.user)
        return Response({"results": data})


class TrendView(APIView):
    def get(self, request):
        days = int(request.query_params.get("days", 7))
        return Response({"results": StatisticsService.trend(request.user, days)})


class HeatmapView(APIView):
    def get(self, request):
        return Response({"results": StatisticsService.heatmap(request.user)})


class KeywordEffectView(APIView):
    def get(self, request):
        return Response({"results": StatisticsService.keyword_effect(request.user)})
