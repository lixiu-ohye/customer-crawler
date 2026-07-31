"""用户 / 角色 / 权限模型"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    """权限点"""

    code = models.CharField("权限编码", max_length=64, unique=True)
    name = models.CharField("权限名称", max_length=64)

    class Meta:
        db_table = "sys_permission"
        verbose_name = "权限"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}({self.code})"


class Role(models.Model):
    """角色"""

    name = models.CharField("角色名称", max_length=32, unique=True)
    code = models.CharField("角色编码", max_length=32, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)

    class Meta:
        db_table = "sys_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    """扩展用户"""

    ROLE_CHOICES = (("member", "会员"), ("admin", "管理员"), ("vip", "VIP会员"))

    phone = models.CharField("手机号", max_length=20, blank=True, default="")
    role_type = models.CharField("角色类型", max_length=16, choices=ROLE_CHOICES, default="member")
    roles = models.ManyToManyField(Role, related_name="users", blank=True)
    plan = models.CharField("套餐", max_length=32, default="free")
    plan_expires = models.DateTimeField("套餐到期时间", null=True, blank=True)
    quota_used = models.IntegerField("已用采集配额", default=0)
    quota_limit = models.IntegerField("采集配额上限", default=1000)

    class Meta:
        db_table = "sys_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    @property
    def is_admin(self):
        return self.role_type == "admin" or self.is_superuser


class UserRole(models.Model):
    """用户-角色关联（冗余表，方便查询）"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_role_links")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_role_links")

    class Meta:
        db_table = "sys_user_role"
        unique_together = ("user", "role")
