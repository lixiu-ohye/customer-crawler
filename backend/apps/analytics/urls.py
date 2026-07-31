"""AI 分析路由"""
from django.urls import path

from apps.analytics.views import BatchRescreenView, LeadAnalysisView, ScriptView

urlpatterns = [
    path("rescreen", BatchRescreenView.as_view()),
    path("script", ScriptView.as_view()),
    path("lead/<int:pk>", LeadAnalysisView.as_view()),
]
