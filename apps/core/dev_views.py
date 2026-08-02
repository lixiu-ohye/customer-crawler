# -*- coding: utf-8 -*-
"""开发者选项接口"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class DevOptionsView(APIView):
    """开发者选项配置"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "result": {
                "username": user.username,
                "role_type": getattr(user, "role_type", "user") or "user",
                "privileges": [
                    {"code": "unlimited", "name": "无限采集", "desc": "不消耗任何额度，并发无上限"},
                    {"code": "unlimited_ai", "name": "无限AI", "desc": "AI摘要/话术不限次数"},
                    {"code": "dev_menu", "name": "开发者菜单", "desc": "专属开发者选项入口"},
                ],
            }
        })
