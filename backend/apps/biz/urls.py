"""企业信息模块路由"""
from django.urls import path

from apps.biz.views import CompanyEventListView, CompanyListView, ContactListView, ScreenTemplateListView

urlpatterns = [
    path("companies", CompanyListView.as_view()),
    path("events", CompanyEventListView.as_view()),
    path("contacts", ContactListView.as_view()),
    path("templates", ScreenTemplateListView.as_view()),
]
