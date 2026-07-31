"""URL 配置"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/keywords/", include("apps.keywords.urls")),
    path("api/crawler/", include("apps.crawler.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/stats/", include("apps.stats.urls")),
    path("api/misc/", include("apps.core.urls")),
]
