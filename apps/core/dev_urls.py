# -*- coding: utf-8 -*-
"""开发者选项路由"""
from django.urls import path

from apps.core.dev_views import DevOptionsView

urlpatterns = [
    path("options", DevOptionsView.as_view()),
]
