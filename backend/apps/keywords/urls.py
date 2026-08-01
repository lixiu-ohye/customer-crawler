"""关键词模块路由"""
from django.urls import path

from apps.keywords.views import (
    IndustryApplyView,
    IndustryLeadsView,
    IndustryLibraryView,
    IndustryNavView,
    IndustryRegionsView,
    IndustryTreeView,
    KeywordBulkView,
    KeywordDetailView,
    KeywordExpandView,
    KeywordGroupView,
    KeywordListView,
    KeywordSuggestView,
    PromoterIndustryView,
)

urlpatterns = [
    path("", KeywordListView.as_view()),
    path("bulk", KeywordBulkView.as_view()),
    path("suggest", KeywordSuggestView.as_view()),
    path("expand", KeywordExpandView.as_view()),
    path("groups", KeywordGroupView.as_view()),
    path("industry-library", IndustryLibraryView.as_view()),
    path("industry-apply", IndustryApplyView.as_view()),
    path("industry-nav", IndustryNavView.as_view()),
    path("industry-leads", IndustryLeadsView.as_view()),
    path("industry-tree", IndustryTreeView.as_view()),
    path("industry-regions", IndustryRegionsView.as_view()),
    path("promoter-industries", PromoterIndustryView.as_view()),
    path("<int:pk>", KeywordDetailView.as_view()),
]
