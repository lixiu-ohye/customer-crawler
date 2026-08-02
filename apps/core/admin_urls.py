# -*- coding: utf-8 -*-
"""系统管理路由（前端 /admin/* 别名）"""
from django.urls import path

from apps.core.admin_views import (
    AdminLogsView,
    AdminModeView,
    AdminParamsView,
    AdminUserDetailView,
    AdminUsersView,
)

urlpatterns = [
    path("users", AdminUsersView.as_view()),
    path("users/<int:pk>", AdminUserDetailView.as_view()),
    path("params", AdminParamsView.as_view()),
    path("logs", AdminLogsView.as_view()),
    path("mode", AdminModeView.as_view()),
]
