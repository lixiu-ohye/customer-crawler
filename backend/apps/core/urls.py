"""核心模块路由"""
from django.urls import path

from apps.core.views import DisclaimerView, IndustryNavigationView, OperationLogView

urlpatterns = [
    path("disclaimer", DisclaimerView.as_view()),
    path("logs", OperationLogView.as_view()),
    path("industry-nav", IndustryNavigationView.as_view()),
]
