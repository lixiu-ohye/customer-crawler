"""分销体系路由"""
from django.urls import path

from apps.distribution.views import (
    AdminPlatformView,
    AdminPromoterFreezeView,
    AdminWithdrawalProcessView,
    AdminWithdrawalsView,
    PromoterApplyView,
    PromoterCommissionsView,
    PromoterMyView,
    PromoterRegisterView,
    PromoterWithdrawView,
)

urlpatterns = [
    path("promotion/my", PromoterMyView.as_view()),
    path("promotion/apply", PromoterApplyView.as_view()),
    path("promotion/commissions", PromoterCommissionsView.as_view()),
    path("promotion/withdraw", PromoterWithdrawView.as_view()),
    path("promotion/register", PromoterRegisterView.as_view()),
    path("admin/platform", AdminPlatformView.as_view()),
    path("admin/promoter/<int:promoter_id>/freeze", AdminPromoterFreezeView.as_view()),
    path("admin/withdrawals", AdminWithdrawalsView.as_view()),
    path("admin/withdrawal/<str:withdrawal_id>", AdminWithdrawalProcessView.as_view()),
]
