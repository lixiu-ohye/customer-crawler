# -*- coding: utf-8 -*-
"""舆情监控模块 URL 配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MonitorTargetViewSet,
    CommentViewSet,
    TriggerRuleViewSet,
    DmTemplateViewSet,
    AccountPoolViewSet,
)

# 创建路由器
router = DefaultRouter()
router.register(r'targets', MonitorTargetViewSet, basename='monitor-target')
router.register(r'comments', CommentViewSet, basename='monitor-comment')
router.register(r'rules', TriggerRuleViewSet, basename='monitor-rule')
router.register(r'templates', DmTemplateViewSet, basename='monitor-template')
router.register(r'accounts', AccountPoolViewSet, basename='monitor-account')

# API URL 配置
urlpatterns = [
    path('', include(router.urls)),
]