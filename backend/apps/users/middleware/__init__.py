"""JWT 认证中间件"""
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from apps.users.models import User


def create_token(user):
    """生成 JWT"""
    from datetime import datetime, timezone

    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role_type,
        "exp": datetime.now(timezone.utc) + settings.JWT_EXPIRES,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class JWTAuthentication(authentication.BaseAuthentication):
    """基于 JWT 的 DRF 认证类"""

    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith(f"{self.keyword} "):
            return None
        token = header[len(self.keyword) + 1 :].strip()
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("登录已过期，请重新登录")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("无效的登录凭证")
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("用户不存在")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("账号已被禁用")
        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
