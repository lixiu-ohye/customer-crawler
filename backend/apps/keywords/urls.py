"""关键词模块路由"""
from django.urls import path

from apps.keywords.views import (
    IndustryApplyView,
    IndustryLibraryView,
    KeywordBulkView,
    KeywordDetailView,
    KeywordExpandView,
    KeywordGroupView,
    KeywordListView,
    KeywordSuggestView,
)

urlpatterns = [
    path("", KeywordListView.as_view()),
    path("bulk", KeywordBulkView.as_view()),
    path("suggest", KeywordSuggestView.as_view()),
    path("expand", KeywordExpandView.as_view()),
    path("groups", KeywordGroupView.as_view()),
    path("industry-library", IndustryLibraryView.as_view()),
    path("industry-apply", IndustryApplyView.as_view()),
    path("<int:pk>", KeywordDetailView.as_view()),
]
