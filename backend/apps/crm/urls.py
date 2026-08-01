"""客户管理模块路由"""
from django.urls import path

from apps.crm.views import ExportAuditLogListView, LeadPoolListView

urlpatterns = [
    path("pool", LeadPoolListView.as_view()),
    path("export-logs", ExportAuditLogListView.as_view()),
]
