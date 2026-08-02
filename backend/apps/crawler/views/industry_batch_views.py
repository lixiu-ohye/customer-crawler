# -*- coding: utf-8 -*-
"""行业关键词批量自动采集视图
POST /api/crawler/industry/batch      {industry, platforms, max_keywords} → 启动批量采集
GET  /api/crawler/industry/batch/<id> → 查询批量任务状态
GET  /api/crawler/industry/batch      → 批量任务列表
GET  /api/crawler/industry/options    → 可选行业+平台（供前端下拉）
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.industry_library import INDUSTRY_LIBRARY, INDUSTRY_DESC, all_words
from apps.crawler.services.industry_batch import (
    start_industry_batch,
    get_batch,
    list_batches,
)


class IndustryBatchView(APIView):
    """行业批量采集任务"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        industry = (request.data.get("industry") or "").strip()
        platforms = request.data.get("platforms") or ["weibo"]
        if isinstance(platforms, str):
            platforms = [p.strip() for p in platforms.split(",") if p.strip()]
        max_keywords = int(request.data.get("max_keywords", 8) or 8)
        max_keywords = max(1, min(max_keywords, 15))

        if not industry:
            return Response({"detail": "请提供行业 industry"}, status=400)

        result = start_industry_batch(
            industry, platforms, max_keywords=max_keywords, user_id=request.user.id
        )
        if result.get("success"):
            return Response(result)
        return Response(result, status=400)

    def get(self, request):
        batch_id = request.query_params.get("id") or ""
        if batch_id:
            result = get_batch(batch_id)
            if result.get("success"):
                return Response(result)
            return Response(result, status=404)
        return Response(list_batches())


class IndustryBatchOptionsView(APIView):
    """行业 + 平台选项（供前端下拉）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        industries = [
            {
                "name": name,
                "description": INDUSTRY_DESC.get(name, ""),
                "word_count": len(all_words(name)),
            }
            for name in INDUSTRY_LIBRARY.keys()
        ]
        platforms = [
            {"code": "weibo", "name": "微博"},
            {"code": "douyin", "name": "抖音"},
            {"code": "xiaohongshu", "name": "小红书"},
            {"code": "kuaishou", "name": "快手"},
            {"code": "zhihu", "name": "知乎"},
            {"code": "tieba", "name": "贴吧"},
        ]
        return Response({"results": {"industries": industries, "platforms": platforms}})
