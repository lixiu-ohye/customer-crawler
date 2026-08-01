"""舆情监控模块路由"""
from django.urls import path

from apps.monitor.views import IntentCommentListView, MonitorTargetListView, TriggerRuleListView

urlpatterns = [
    path("targets", MonitorTargetListView.as_view()),
    path("intent-comments", IntentCommentListView.as_view()),
    path("trigger-rules", TriggerRuleListView.as_view()),
]
