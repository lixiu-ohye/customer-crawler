"""用户模块路由"""
from django.urls import path

from apps.users.views import LoginView, ProfileView, RegisterView, UpdatePlanView

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("profile", ProfileView.as_view()),
    path("plan", UpdatePlanView.as_view()),
]
