"""认证视图：登录 / 注册 / 用户资料"""
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.middleware import create_token
from apps.users.models import User
from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = create_token(user)
        return Response(
            {"token": token, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = create_token(user)
        return Response({"token": token, "user": UserSerializer(user).data})


class ProfileView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        for field in ("phone", "email"):
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(UserSerializer(user).data)


class UpdatePlanView(APIView):
    """套餐变更（会员中心）"""

    def post(self, request):
        user = request.user
        plan = request.data.get("plan", "")
        if plan not in ("free", "basic", "pro", "vip"):
            return Response({"detail": "无效套餐"}, status=status.HTTP_400_BAD_REQUEST)
        user.plan = plan
        user.plan_expires = timezone.now() + timezone.timedelta(days=30)
        user.quota_limit = {"free": 1000, "basic": 5000, "pro": 20000, "vip": 100000}.get(plan, 1000)
        user.save()
        return Response(UserSerializer(user).data)
