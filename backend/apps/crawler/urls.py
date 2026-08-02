"""爬虫模块路由"""
from django.urls import path

from apps.crawler.views.official_api_views import (
    OfficialPlatformsView,
    OfficialSearchView,
    OfficialAuditView,
    OfficialCredentialsView,
)
from apps.crawler.views import CrawlerConfigView, ModeSwitchView, PlatformStatusView
from apps.crawler.views.realdata_views import (
    MediaCrawlerImportView,
    RealLeadsView,
)
from apps.crawler.views.mediacrawler_views import (
    MediaCrawlerTaskView,
    MediaCrawlerTaskDetailView,
    MediaCrawlerTaskResultView,
    MediaCrawlerPlatformsView,
    MediaCrawlerQuickStartView
)
from apps.crawler.views.industry_batch_views import (
    IndustryBatchView,
    IndustryBatchOptionsView,
)

urlpatterns = [
    # 官方开放 API 合规采集路由
    path("official/platforms", OfficialPlatformsView.as_view(), name="official_platforms"),
    path("official/search", OfficialSearchView.as_view(), name="official_search"),
    path("official/audit", OfficialAuditView.as_view(), name="official_audit"),
    path("official/credentials", OfficialCredentialsView.as_view(), name="official_credentials"),
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
    # 真实数据导入
    path("mediacrawler/import", MediaCrawlerImportView.as_view(), name="mc_import"),
    path("realleads", RealLeadsView.as_view(), name="real_leads"),
    # 行业关键词批量自动采集
    path("industry/batch", IndustryBatchView.as_view(), name="industry_batch"),
    path("industry/options", IndustryBatchOptionsView.as_view(), name="industry_batch_options"),

]
