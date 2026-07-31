# -*- coding: utf-8 -*-
"""行业导航与获客词库：12 行业导航 / 词库查询 / 推广员关注行业"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.industry_library import INDUSTRY_LIBRARY, INDUSTRY_DESC
from apps.keywords.models import PromoterIndustry


class IndustryNavView(APIView):
    """行业导航：12 行业列表（含描述/预览词）+ 单行业词库

    GET /keywords/industry-nav              → { results: { industries: [{id,name,description,preview}], cities: [...] } }
    GET /keywords/industry-nav?industry=X   → { results: { industry, description, mainWords, longTailWords, negativeWords, globalNegativeWords, allNegativeWords } }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        industry = (request.query_params.get("industry") or "").strip()
        if industry:
            lib = INDUSTRY_LIBRARY.get(industry)
            if not lib:
                return Response({"detail": f"未知行业: {industry}"}, status=404)
            from apps.keywords.industry_library import (
                GLOBAL_NEGATIVE_WORDS,
                all_negative_words,
            )
            return Response({
                "result": {
                    "industry": industry,
                    "description": INDUSTRY_DESC.get(industry, ""),
                    "mainWords": lib["mainWords"],
                    "longTailWords": lib["longTailWords"],
                    "negativeWords": lib["negativeWords"],
                    "globalNegativeWords": GLOBAL_NEGATIVE_WORDS,
                    "allNegativeWords": all_negative_words(industry),
                }
            })
        industries = [
            {
                "id": i + 1,
                "name": name,
                "description": INDUSTRY_DESC.get(name, ""),
                "preview": INDUSTRY_LIBRARY[name]["mainWords"][:4],
            }
            for i, name in enumerate(INDUSTRY_LIBRARY.keys())
        ]
        return Response({"result": {"industries": industries}})


class PromoterIndustryView(APIView):
    """推广员关注行业

    GET  /keywords/promoter-industries   → { results: { industries: [{id,name,description}] } }
    POST /keywords/promoter-industries   body: { industryIds: [1,2,3] } → 全量替换
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        follows = PromoterIndustry.objects.filter(user=request.user).select_related("user")
        industries = [
            {
                "id": f.industry_id,
                "name": f.industry_name,
                "description": INDUSTRY_DESC.get(f.industry_name, ""),
            }
            for f in follows
        ]
        return Response({"result": {"industries": industries}})

    def post(self, request):
        industry_ids = request.data.get("industryIds") or []
        name_by_id = {
            i + 1: name for i, name in enumerate(INDUSTRY_LIBRARY.keys())
        }
        # 全量替换
        PromoterIndustry.objects.filter(user=request.user).delete()
        created = 0
        for iid in industry_ids:
            try:
                iid = int(iid)
            except (TypeError, ValueError):
                continue
            name = name_by_id.get(iid)
            if not name:
                continue
            _, is_new = PromoterIndustry.objects.get_or_create(
                user=request.user, industry_id=iid,
                defaults={"industry_name": name},
            )
            if is_new:
                created += 1
        return Response({
            "result": {"saved": created, "industryIds": [int(x) for x in industry_ids]},
        })
