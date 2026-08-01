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


class OfficialCredentialsView(APIView):
    """
    凭证热配置接口 (仅管理员):
      GET    /api/crawler/official/credentials            查看当前配置状态 (凭证打码)
      POST   /api/crawler/official/credentials            写入/更新某平台凭证 (存 Redis 热生效)
        body: {"platform": "douyin", "credentials": {"client_key": "...", "client_secret": "..."}}
      DELETE /api/crawler/official/credentials?platform=xxx   清除某平台 Redis 凭证 (回退 settings/env)
    """

    permission_classes = [IsAuthenticated]

    def _is_staff(self, request) -> bool:
        return bool(request.user and getattr(request.user, "is_staff", False))

    def get(self, request):
        from apps.crawler.official_apis.base import OfficialAPIAdapter

        redis_creds = OfficialAPIAdapter._redis_get_credentials()
        out = {}
        for platform, creds in redis_creds.items():
            masked = {k: (v[:3] + "***" + v[-2:] if len(v) > 6 else "***") for k, v in creds.items() if v}
            out[platform] = {"source": "redis", "credentials": masked}
        for platform in PLATFORM_NAMES:
            if platform not in out:
                adapter = AdapterRegistry.get(platform)
                if adapter and adapter.is_configured:
                    out[platform] = {"source": "settings/env", "credentials": {}}
                else:
                    out[platform] = {"source": "none", "credentials": {}}
        return Response({"results": out})

    def post(self, request):
        if not self._is_staff(request):
            return Response({"detail": "仅管理员可配置凭证"}, status=403)
        platform = str(request.data.get("platform", "")).lower()
        creds = request.data.get("credentials") or {}
        if platform not in PLATFORM_NAMES or not isinstance(creds, dict):
            return Response({"detail": "平台或凭证格式无效"}, status=400)
        from apps.crawler.official_apis.base import OfficialAPIAdapter

        ok = OfficialAPIAdapter.set_credentials(platform, creds)
        if not ok:
            return Response({"detail": "写入失败 (Redis 不可用?)"}, status=500)
        adapter = AdapterRegistry.get(platform)
        return Response({
            "ok": True,
            "platform": platform,
            "mode": adapter.mode if adapter else "unknown",
            "configured": adapter.is_configured if adapter else False,
        })

    def delete(self, request):
        if not self._is_staff(request):
            return Response({"detail": "仅管理员可配置凭证"}, status=403)
        platform = str(request.query_params.get("platform", "")).lower()
        if platform not in PLATFORM_NAMES:
            return Response({"detail": "平台无效"}, status=400)
        from apps.crawler.official_apis.base import OfficialAPIAdapter

        OfficialAPIAdapter.clear_credentials(platform)
        adapter = AdapterRegistry.get(platform)
        return Response({
            "ok": True,
            "platform": platform,
            "mode": adapter.mode if adapter else "demo",
        })
