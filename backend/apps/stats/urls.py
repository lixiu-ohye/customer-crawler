"""统计模块路由"""
from django.urls import path

from apps.stats.views import DashboardView, DistributionView, HeatmapView, KeywordEffectView, TrendView

urlpatterns = [
    path("dashboard", DashboardView.as_view()),
    path("distribution", DistributionView.as_view()),
    path("trend", TrendView.as_view()),
    path("heatmap", HeatmapView.as_view()),
    path("keyword-effect", KeywordEffectView.as_view()),
]
