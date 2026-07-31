"""爬虫视图：平台状态、模式切换"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crawler.services.adapter import adapter_service
from apps.crawler.services.crawler_service import CrawlerService
from django.conf import settings


class PlatformStatusView(APIView):
    """各平台采集状态"""

    def get(self, request):
        return Response({"results": adapter_service.get_platform_status()})


class ModeSwitchView(APIView):
    """爬虫 / API 模式切换"""

    def get(self, request):
        return Response({"result": {"mode": adapter_service.get_mode()}})

    def post(self, request):
        mode = request.data.get("mode", "")
        if adapter_service.set_mode(mode):
            return Response({"result": {"mode": adapter_service.get_mode()}})
        return Response({"detail": "无效模式"}, status=400)


class CrawlerConfigView(APIView):
    """爬虫风控配置查看"""

    def get(self, request):
        return Response({"result": settings.CRAWLER_SETTINGS})
