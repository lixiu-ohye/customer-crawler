"""爬虫模块路由"""
from django.urls import path

from apps.crawler.views import CrawlerConfigView, ModeSwitchView, PlatformStatusView
from apps.crawler.views.mediacrawler_views import (
    MediaCrawlerTaskView,
    MediaCrawlerTaskDetailView,
    MediaCrawlerTaskResultView,
    MediaCrawlerPlatformsView,
    MediaCrawlerQuickStartView
)

urlpatterns = [
    # 原有路由
    path("platforms", PlatformStatusView.as_view()),
    path("mode", ModeSwitchView.as_view()),
    path("config", CrawlerConfigView.as_view()),
    
    # MediaCrawler 集成路由
    path("mediacrawler/tasks", MediaCrawlerTaskView.as_view(), name="mc_tasks"),
    path("mediacrawler/tasks/<str:task_id>", MediaCrawlerTaskDetailView.as_view(), name="mc_task_detail"),
    path("mediacrawler/tasks/<str:task_id>/results", MediaCrawlerTaskResultView.as_view(), name="mc_task_results"),
    path("mediacrawler/platforms", MediaCrawlerPlatformsView.as_view(), name="mc_platforms"),
    path("mediacrawler/quickstart", MediaCrawlerQuickStartView.as_view(), name="mc_quickstart"),
]
