# -*- coding: utf-8 -*-
"""行业词库 API：词库查询 / 一键应用（导入关键词）"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.industry_library import (
    INDUSTRY_LIBRARY,
    all_negative_words,
    all_words,
    industry_names,
)
from apps.keywords.models import Keyword, KeywordGroup


class IndustryLibraryView(APIView):
    """行业词库查询

    GET  /keywords/industry-library            → 全部行业名 + 全局否定词
    GET  /keywords/industry-library?industry=X → 该行业主词/长尾词/否定词
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        industry = (request.query_params.get("industry") or "").strip()
        if industry:
            lib = INDUSTRY_LIBRARY.get(industry)
            if not lib:
                return Response({"detail": f"未知行业: {industry}"}, status=404)
            return Response({
                "result": {
                    "industry": industry,
                    "mainWords": lib["mainWords"],
                    "longTailWords": lib["longTailWords"],
                    "negativeWords": lib["negativeWords"],
                    "globalNegativeWords": [
                        w for w in __import__("apps.keywords.industry_library", fromlist=["GLOBAL_NEGATIVE_WORDS"]).GLOBAL_NEGATIVE_WORDS
                    ],
                    "allNegativeWords": all_negative_words(industry),
                }
            })
        return Response({
            "result": {
                "industries": industry_names(),
                "globalNegativeWords": __import__(
                    "apps.keywords.industry_library", fromlist=["GLOBAL_NEGATIVE_WORDS"]
                ).GLOBAL_NEGATIVE_WORDS,
            }
        })


class IndustryApplyView(APIView):
    """一键应用行业词库：将某行业全部词导入当前用户关键词（按行业分组）

    POST /keywords/industry-apply  body: {"industry": "装修家居"}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        industry = (request.data.get("industry") or "").strip()
        if not industry or industry not in INDUSTRY_LIBRARY:
            return Response({"detail": "请提供有效的行业名"}, status=400)

        group, _ = KeywordGroup.objects.get_or_create(
            user=request.user, name=f"行业词库-{industry}"
        )
        neg_words = ",".join(all_negative_words(industry))
        words = all_words(industry)
        created, skipped = 0, 0
        for w in words:
            _, is_new = Keyword.objects.get_or_create(
                user=request.user, word=w,
                defaults={"group": group, "negative_words": neg_words, "hot_score": 80},
            )
            if is_new:
                created += 1
            else:
                skipped += 1
        return Response({
            "result": {
                "industry": industry,
                "created": created,
                "skipped": skipped,
                "group": {"id": group.id, "name": group.name},
            }
        })
