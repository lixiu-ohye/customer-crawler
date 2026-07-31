"""合规操作日志中间件：记录写操作"""
import logging

logger = logging.getLogger(__name__)


class ComplianceLogMiddleware:
    """记录所有非 GET 请求的操作日志"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if request.method not in ("GET", "HEAD", "OPTIONS") and getattr(request, "user", None) and request.user.is_authenticated:
                from apps.core.services import log_operation

                path = request.path
                # 排除认证与日志类路径，避免噪音
                if not any(skip in path for skip in ("/api/auth/login", "/api/auth/register", "/api/misc/logs")):
                    log_operation(
                        request.user,
                        action=f"{request.method} {path}",
                        detail=str(getattr(request, "data", "") or "")[:200],
                        ip=request.META.get("REMOTE_ADDR", ""),
                    )
        except Exception:
            logger.exception("compliance middleware error")
        return response
