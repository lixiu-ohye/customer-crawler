"""URL 配置"""
from django.contrib import admin
from django.urls import include, path

# 别名路由视图（复用原实现）
from apps.distribution.views import (
    AdminPlatformView as AdminPlatformAlias,
    AdminWithdrawalProcessView as AdminWithdrawalAlias,
    PromoterApplyView as PromoterApplyAlias,
    PromoterCommissionsView as PromoterCommissionsAlias,
    PromoterMyView as PromoterMyAlias,
    PromoterWithdrawView as PromoterWithdrawAlias,
)
from apps.distribution.pay_views import PromotionPayView

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
    path("api/biz/", include("apps.biz.urls")),
    path("api/crm/", include("apps.crm.urls")),
    path("api/monitor/", include("apps.monitor.urls")),
    path("api/commerce/", include("apps.commerce.urls")),
    path("api/distribution/", include("apps.distribution.urls")),
    # ---- 别名路由：对齐前端调用路径 ----
    path("api/admin/", include("apps.core.admin_urls")),
    path("api/dev/", include("apps.core.dev_urls")),
    path("api/promotion/my", PromoterMyAlias.as_view()),
    path("api/promotion/commissions", PromoterCommissionsAlias.as_view()),
    path("api/promotion/apply", PromoterApplyAlias.as_view()),
    path("api/promotion/withdraw", PromoterWithdrawAlias.as_view()),
    path("api/promotion/pay", PromotionPayView.as_view()),
    path("api/admin/platform", AdminPlatformAlias.as_view()),
    path("api/admin/withdrawal/<str:withdrawal_id>", AdminWithdrawalAlias.as_view()),
    path("api/analysis/", include("apps.analytics.urls")),
]
