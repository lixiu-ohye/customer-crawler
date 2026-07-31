"""核心视图：免责声明、操作日志、行业地点导航"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.services import DISCLAIMER_TEXT, OperationLog
from apps.keywords.services import KeywordService


class DisclaimerView(APIView):
    """合规免责声明"""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"result": {"text": DISCLAIMER_TEXT, "accepted": False}})


class OperationLogView(APIView):
    """操作日志查询"""

    def get(self, request):
        logs = OperationLog.objects.filter(user=request.user)[:200]
        return Response({
            "results": [
                {"id": l.id, "action": l.action, "detail": l.detail,
                 "ip": l.ip or "", "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S")}
                for l in logs
            ]
        })


class IndustryNavigationView(APIView):
    """大数据行业地点导航 + 自动联想：行业 → 城市 → 组合关键词"""

    permission_classes = [AllowAny]

    def get(self, request):
        industry = request.query_params.get("industry", "")
        city = request.query_params.get("city", "")
        if industry and industry in KeywordService.INDUSTRY_DICT:
            words = KeywordService.INDUSTRY_DICT[industry]
            if city:
                suggestions = [f"{city}{w}" for w in words] + words
            else:
                suggestions = words
            return Response({"results": {"industry": industry, "city": city, "keywords": suggestions}})
        # 返回全部行业与城市目录
        return Response({
            "results": {
                "industries": list(KeywordService.INDUSTRY_DICT.keys()),
                "cities": KeywordService.CITY_DICT,
            }
        })
