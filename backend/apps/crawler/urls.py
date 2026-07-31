"""爬虫模块路由"""
from django.urls import path

from apps.crawler.views import CrawlerConfigView, ModeSwitchView, PlatformStatusView

urlpatterns = [
    path("platforms", PlatformStatusView.as_view()),
    path("mode", ModeSwitchView.as_view()),
    path("config", CrawlerConfigView.as_view()),
]
