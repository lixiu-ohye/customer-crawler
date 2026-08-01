"""
JWT 认证和权限控制模块
扩展 Django 自带认证系统，支持 JWT Token
"""
import jwt
import datetime
import logging
from typing import Optional, Dict, Any, List
from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

User = get_user_model()

# JWT 配置
JWT_SECRET = getattr(settings, 'JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_HOURS = 24


class JWTAuthentication(authentication.BaseAuthentication):
    """JWT 认证类"""
    
    def authenticate(self, request):
        """认证请求"""
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # 去掉 "Bearer " 前缀
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token 已过期')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'无效的 Token: {str(e)}')
        
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token 缺少用户ID')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('用户不存在')
        
        return (user, token)
    
    def authenticate_header(self, request):
        return 'Bearer'


def generate_token(user, expires_in: int = JWT_EXPIRE_HOURS) -> str:
    """
    生成 JWT Token
    
    Args:
        user: Django User 实例
        expires_in: 过期小时数
        
    Returns:
        JWT Token 字符串
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': getattr(user, 'role_type', 'member'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    """
    验证 JWT Token
    
    Args:
        token: JWT Token 字符串
        
    Returns:
        payload 字典 或 None
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning('Token 已过期')
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f'无效 Token: {e}')
        return None


class IsDeveloper(permissions.BasePermission):
    """开发者权限检查"""
    
    message = '需要开发者权限'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查是否是开发者
        if hasattr(request.user, 'is_developer') and request.user.is_developer:
            return True
        
        # 检查是否是超级用户
        if request.user.is_superuser:
            return True
        
        # 检查角色
        if getattr(request.user, 'role_type', '') == 'admin':
            return True
        
        return False


class IsVIP(permissions.BasePermission):
    """VIP 用户权限"""
    
    message = '需要 VIP 权限'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查是否是 VIP
        if hasattr(request.user, 'is_vip'):
            return request.user.is_vip
        
        # 检查套餐
        plan = getattr(request.user, 'plan', 'free')
        return plan in ('vip', 'enterprise', 'developer')
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """所有者或只读权限"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查是否是对象所有者
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


def token_required(func):
    """装饰器：要求有效的 JWT Token"""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        auth = JWTAuthentication()
        result = auth.authenticate(request)
        
        if result is None:
            raise AuthenticationFailed('请先登录')
        
        request.user, request.auth = result
        return func(self, request, *args, **kwargs)
    
    return wrapper


def role_required(allowed_roles: List[str]):
    """装饰器：角色权限检查"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                raise AuthenticationFailed('请先登录')
            
            user_role = getattr(request.user, 'role_type', 'member')
            if user_role not in allowed_roles:
                if not request.user.is_superuser:
                    raise PermissionDenied(f'需要 {", ".join(allowed_roles)} 权限')
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# 权限检查函数
def check_permission(user, permission: str) -> bool:
    """
    检查用户权限
    
    Args:
        user: Django User 实例
        permission: 权限标识
        
    Returns:
        是否有权限
    """
    if not user or not user.is_authenticated:
        return False
    
    # 超级用户拥有所有权限
    if user.is_superuser:
        return True
    
    # 定义权限映射
    permission_map = {
        'read:data': ['member', 'vip', 'admin'],
        'write:data': ['vip', 'admin'],
        'delete:data': ['admin'],
        'manage:users': ['admin'],
        'manage:roles': ['admin'],
        'manage:api': ['admin', 'developer'],
        'export:data': ['vip', 'admin'],
        'view:analytics': ['vip', 'admin'],
    }
    
    allowed_roles = permission_map.get(permission, [])
    user_role = getattr(user, 'role_type', 'member')
    
    return user_role in allowed_roles