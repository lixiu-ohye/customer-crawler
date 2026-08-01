"""核心模块路由"""
from django.urls import path

from apps.core.views import DisclaimerView, IndustryNavigationView, OperationLogView
from apps.keywords.views import IndustryLeadsView, IndustryRegionsView, IndustryTreeView

urlpatterns = [
    path("disclaimer", DisclaimerView.as_view()),
    path("logs", OperationLogView.as_view()),
    path("industry-nav", IndustryNavigationView.as_view()),
    path("industry-leads", IndustryLeadsView.as_view()),
    path("industry-regions", IndustryRegionsView.as_view()),
    path("industry-tree", IndustryTreeView.as_view()),
]
