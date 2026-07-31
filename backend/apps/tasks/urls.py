"""任务模块路由"""
from django.urls import path

from apps.tasks.views import TaskDetailView, TaskListView

urlpatterns = [
    path("", TaskListView.as_view()),
    path("<int:pk>", TaskDetailView.as_view()),
]
