"""商业化模块路由"""
from django.urls import path

from apps.commerce.views import PlanDefinitionListView, ServicePurchaseListView, UserQuotaListView

urlpatterns = [
    path("plans", PlanDefinitionListView.as_view()),
    path("purchases", ServicePurchaseListView.as_view()),
    path("quotas", UserQuotaListView.as_view()),
]
