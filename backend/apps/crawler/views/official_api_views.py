# -*- coding: utf-8 -*-
"""
官方开放 API 视图层
==================
对外提供统一 REST 接口, 前端无需区分平台差异:

  GET  /api/crawler/official/platforms          平台列表与凭证配置状态
  GET  /api/crawler/official/search?platform=&keyword=&limit=   合规搜索(跨平台)
  POST /api/crawler/official/search             JSON body 批量搜索
  GET  /api/crawler/official/audit              采集审计日志(合规留痕)

所有接口均经过认证 (JWT), 返回结构兼容前端 mock.js。
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crawler.official_apis.base import AdapterRegistry, OfficialAPIError
from apps.crawler.official_apis import platforms as _official_platforms  # noqa: F401 触发适配器注册
from apps.crawler.services.audit_log import get_audit_records

# 平台映射 (与前端一致)
PLATFORM_NAMES = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "kuaishou": "快手",
    "weibo": "微博",
    "zhihu": "知乎",
    "tieba": "贴吧",
}

# 合规声明 (随平台列表返回, 前端可展示)
COMPLIANCE_DECLARATION = {
    "channels": "仅使用各平台官方开放 API / 公开接口",
    "sensitive_data": "不采集手机号/微信号/私信/真实姓名等个人敏感信息",
    "actions": "不自动私信/不批量评论/不破解风控",
    "retention_days": 30,
    "audit": True,
}


class OfficialPlatformsView(APIView):
    """平台列表 + 凭证配置状态 + 合规声明"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        platforms = AdapterRegistry.platforms()
        # 补充中文名
        for p in platforms:
            p["name"] = PLATFORM_NAMES.get(p["platform"], p.get("name", p["platform"]))
        return Response({
            "results": platforms,
            "compliance": COMPLIANCE_DECLARATION,
        })


class OfficialSearchView(APIView):
    """合规搜索接口: GET 单平台 / POST 批量"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        platform = request.query_params.get("platform", "").lower()
        keyword = request.query_params.get("keyword", "").strip()
        limit = min(int(request.query_params.get("limit", 10)), 50)
        if not keyword:
            return Response({"detail": "请提供关键词 keyword"}, status=400)
        if platform not in PLATFORM_NAMES:
            return Response({
                "detail": f"不支持的平台: {platform}",
                "supported_platforms": list(PLATFORM_NAMES.keys()),
            }, status=400)
        adapter = AdapterRegistry.get(platform)
        if not adapter:
            return Response({"detail": f"平台适配器未注册: {platform}"}, status=500)
        try:
            results = adapter.search(keyword, limit=limit)
        except OfficialAPIError as exc:
            return Response({"detail": str(exc), "platform": platform}, status=502)
        return Response({
            "results": results,
            "platform": platform,
            "platform_name": PLATFORM_NAMES[platform],
            "mode": adapter.mode,
            "keyword": keyword,
            "total": len(results),
        })

    def post(self, request):
        """批量搜索: {"searches": [{"platform": "douyin", "keyword": "法律咨询", "limit": 5}, ...]}"""
        searches = request.data.get("searches") or request.data.get("items") or []
        if not isinstance(searches, list) or not searches:
            return Response({"detail": "请提供 searches 数组"}, status=400)

        out = []
        for item in searches:
            platform = str(item.get("platform", "")).lower()
            keyword = str(item.get("keyword", "")).strip()
            limit = min(int(item.get("limit", 10)), 50)
            if not keyword or platform not in PLATFORM_NAMES:
                out.append({"platform": platform, "keyword": keyword, "error": "参数无效"})
                continue
            adapter = AdapterRegistry.get(platform)
            try:
                results = adapter.search(keyword, limit=limit)
                out.append({
                    "platform": platform,
                    "platform_name": PLATFORM_NAMES[platform],
                    "keyword": keyword,
                    "mode": adapter.mode,
                    "results": results,
                    "total": len(results),
                })
            except OfficialAPIError as exc:
                out.append({"platform": platform, "keyword": keyword, "error": str(exc)})
        return Response({"results": out})


class OfficialAuditView(APIView):
    """采集审计日志 (合规留痕)"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 100)), 500)
        return Response({"results": get_audit_records(limit)})
