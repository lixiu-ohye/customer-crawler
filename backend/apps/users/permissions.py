"""
权限管理模块 - 基于角色的访问控制 (RBAC)
"""
import logging
from typing import List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()

# 预定义权限常量
PERMISSIONS = {
    # 数据权限
    'read:data': '读取数据',
    'write:data': '写入数据',
    'delete:data': '删除数据',
    'export:data': '导出数据',
    
    # 用户权限
    'manage:users': '管理用户',
    'view:users': '查看用户',
    
    # 角色权限
    'manage:roles': '管理角色',
    
    # API 权限
    'manage:api': 'API 管理',
    'view:analytics': '查看分析数据',
    
    # 爬虫权限
    'run:crawler': '运行爬虫',
    'manage:crawler': '管理爬虫任务',
    
    # 开发者权限
    'dev:access': '开发者入口',
    'dev:debug': '调试功能',
}


@dataclass
class Role:
    """角色定义"""
    name: str
    code: str
    permissions: Set[str] = field(default_factory=set)
    description: str = ''
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
    
    def add_permission(self, permission: str):
        self.permissions.add(permission)
    
    def remove_permission(self, permission: str):
        self.permissions.discard(permission)


# 预定义角色
ROLE_DEFINITIONS = {
    'guest': Role(
        name='访客',
        code='guest',
        permissions={'read:data'},
        description='只能浏览公开数据'
    ),
    'member': Role(
        name='普通会员',
        code='member',
        permissions={'read:data', 'write:data', 'view:users'},
        description='基础用户权限'
    ),
    'vip': Role(
        name='VIP 会员',
        code='vip',
        permissions={'read:data', 'write:data', 'delete:data', 'export:data', 'view:analytics', 'run:crawler'},
        description='VIP 用户权限'
    ),
    'admin': Role(
        name='管理员',
        code='admin',
        permissions=set(PERMISSIONS.keys()),
        description='管理员权限'
    ),
    'developer': Role(
        name='开发者',
        code='developer',
        permissions={'read:data', 'write:data', 'export:data', 'view:analytics', 'run:crawler', 'manage:crawler', 'dev:access', 'dev:debug'},
        description='开发者权限'
    ),
}


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.roles = ROLE_DEFINITIONS.copy()
    
    def get_role(self, role_code: str) -> Optional[Role]:
        """获取角色定义"""
        return self.roles.get(role_code)
    
    def get_user_permissions(self, user) -> Set[str]:
        """获取用户的全部权限"""
        if not user or not user.is_authenticated:
            return self.roles['guest'].permissions.copy()
        
        # 超级用户拥有所有权限
        if user.is_superuser:
            return set(PERMISSIONS.keys())
        
        # 获取用户角色
        role_type = getattr(user, 'role_type', 'member')
        role = self.roles.get(role_type, self.roles['member'])
        
        # 检查开发者标记
        permissions = role.permissions.copy()
        if hasattr(user, 'is_developer') and user.is_developer:
            permissions.add('dev:access')
            permissions.add('dev:debug')
        
        return permissions
    
    def check_permission(self, user, permission: str) -> bool:
        """检查用户是否有特定权限"""
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def filter_by_permission(self, user, objects: list, permission: str, owner_field: str = 'user') -> list:
        """根据权限过滤对象列表"""
        if not user or not user.is_authenticated:
            return []
        
        # 管理员和超级用户可以看到全部
        if user.is_superuser:
            return objects
        
        role_type = getattr(user, 'role_type', 'member')
        if role_type == 'admin':
            return objects
        
        # 检查权限
        if not self.check_permission(user, permission):
            return []
        
        # 过滤：返回自己的数据 + 公开数据
        result = []
        for obj in objects:
            if hasattr(obj, owner_field):
                if getattr(obj, owner_field) == user:
                    result.append(obj)
            elif hasattr(obj, 'is_public') and obj.is_public:
                result.append(obj)
            else:
                result.append(obj)  # 默认显示
        
        return result
    
    def get_role_options(self) -> List[dict]:
        """获取角色选项列表"""
        return [
            {
                'code': code,
                'name': role.name,
                'description': role.description,
                'permissions': list(role.permissions)
            }
            for code, role in self.roles.items()
        ]
    
    def get_permission_options(self) -> List[dict]:
        """获取权限选项列表"""
        return [
            {'code': code, 'name': name}
            for code, name in PERMISSIONS.items()
        ]


# 全局权限管理器实例
_permission_manager = None


def get_permission_manager() -> PermissionManager:
    """获取权限管理器"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


# 便捷函数
def has_permission(user, permission: str) -> bool:
    """检查用户权限"""
    return get_permission_manager().check_permission(user, permission)


def get_user_permissions(user) -> Set[str]:
    """获取用户权限列表"""
    return get_permission_manager().get_user_permissions(user)