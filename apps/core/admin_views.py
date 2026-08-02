# -*- coding: utf-8 -*-
"""系统管理接口：用户管理 / 参数配置 / 日志 / 模式切换"""
import json
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model

User = get_user_model()

# 参数配置存储（JSON 字段，用 core 配置或内存兜底；这里用数据库 core app 的配置模型不可靠时退化为内存 + 文件持久化）
import os
_PARAMS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "backend", ".admin_params.json")
_DEFAULT_PARAMS = {
    "min_interval": 3,
    "max_per_minute": 20,
    "retry_times": 3,
    "high_intent_threshold": 60,
    "retention_days": 30,
    "mode": "mock",
}


def _load_params():
    try:
        if os.path.exists(_PARAMS_FILE):
            with open(_PARAMS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {**_DEFAULT_PARAMS, **data}
    except Exception:
        pass
    return dict(_DEFAULT_PARAMS)


def _save_params(params):
    try:
        os.makedirs(os.path.dirname(_PARAMS_FILE), exist_ok=True)
        with open(_PARAMS_FILE, "w", encoding="utf-8") as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class AdminUsersView(APIView):
    """用户列表/创建"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "")
        qs = User.objects.all()
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
        results = []
        for u in qs.order_by("-date_joined")[:200]:
            results.append({
                "id": u.id,
                "username": u.username,
                "nickname": getattr(u, "nickname", "") or u.first_name or u.username,
                "email": u.email or "",
                "phone": getattr(u, "phone", "") or "",
                "role_type": getattr(u, "role_type", "user") or "user",
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "plan": {
                    "plan_type": getattr(u, "plan", "free") or "free",
                    "quota_used": getattr(u, "quota_used", 0) or 0,
                    "quota_total": getattr(u, "quota_limit", 1000) or 1000,
                    "expire_at": (u.plan_expires.isoformat() if getattr(u, "plan_expires", None) else "") or "",
                    "concurrent_tasks": 5,
                    "daily_crawl_limit": 500,
                    "api_access": bool(u.is_staff or u.is_superuser),
                },
                "created_at": u.date_joined.strftime("%Y-%m-%d %H:%M:%S") if u.date_joined else "",
            })
        return Response({"results": results, "total": len(results)})

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        if not username:
            return Response({"detail": "用户名必填"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"detail": "用户名已存在"}, status=400)
        u = User(username=username, email=request.data.get("email", ""), is_active=True)
        u.set_password(password or "123456")
        u.role_type = request.data.get("role_type", "user") or "user"
        # users.0002 新增字段（显式设置避免 NOT NULL 错误）
        if hasattr(u, "is_developer"):
            u.is_developer = False
        if hasattr(u, "developer_note"):
            u.developer_note = ""
        if hasattr(u, "developer_expires"):
            u.developer_expires = None
        u.save()
        return Response({"result": {"id": u.id, "username": u.username}}, status=201)


class AdminUserDetailView(APIView):
    """用户编辑/启停"""
    permission_classes = [IsAuthenticated]

    def _get(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def put(self, request, pk):
        u = self._get(pk)
        if not u:
            return Response({"detail": "用户不存在"}, status=404)
        if request.data.get("nickname"):
            u.first_name = request.data["nickname"]
        if "email" in request.data:
            u.email = request.data.get("email", "")
        if "role_type" in request.data:
            u.role_type = request.data["role_type"]
        if request.data.get("password"):
            u.set_password(request.data["password"])
        u.save()
        return Response({"result": {"id": u.id, "username": u.username}})

    def post(self, request, pk):
        u = self._get(pk)
        if not u:
            return Response({"detail": "用户不存在"}, status=404)
        action = request.data.get("action")
        if action == "toggle":
            u.is_active = not u.is_active
            u.save()
            return Response({"result": {"id": u.id, "is_active": u.is_active}})
        return Response({"detail": "未知操作"}, status=400)


class AdminParamsView(APIView):
    """参数配置"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"result": _load_params()})

    def post(self, request):
        params = _load_params()
        for k, v in (request.data or {}).items():
            params[k] = v
        _save_params(params)
        return Response({"result": params})


class AdminLogsView(APIView):
    """日志管理"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        log_type = request.query_params.get("type", "")
        # 优先读 core OperationLog；无则返回空
        try:
            from apps.core.models import OperationLog
            qs = OperationLog.objects.all()
            if log_type:
                qs = qs.filter(type=log_type)
            results = [
                {"id": l.id, "type": getattr(l, "type", "operation") or "operation",
                 "action": l.action or "", "detail": l.detail or "",
                 "ip": getattr(l, "ip", "") or "", "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else ""}
                for l in qs.order_by("-created_at")[:200]
            ]
            return Response({"results": results, "total": len(results)})
        except Exception:
            return Response({"results": [], "total": 0})


class AdminModeView(APIView):
    """模式切换（crawler/api/mock）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"result": {"mode": _load_params().get("mode", "mock")}})

    def post(self, request):
        mode = request.data.get("mode", "mock")
        params = _load_params()
        params["mode"] = mode
        _save_params(params)
        return Response({"result": {"mode": mode}})
