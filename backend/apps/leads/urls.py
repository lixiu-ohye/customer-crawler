"""线索模块路由"""
from django.urls import path

from apps.leads.views import LeadBatchView, LeadDetailView, LeadExportView, LeadListView

urlpatterns = [
    path("", LeadListView.as_view()),
    path("export", LeadExportView.as_view()),
    path("batch", LeadBatchView.as_view()),
    path("<int:pk>", LeadDetailView.as_view()),
]
