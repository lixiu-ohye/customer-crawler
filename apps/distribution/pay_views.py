# -*- coding: utf-8 -*-
"""推广支付接口（模拟支付，标记订单已支付并开通体验包）"""
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.distribution.models import DistributionOrder


class PromotionPayView(APIView):
    """模拟支付：按 orderId 标记订单已支付（体验包开通）"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("orderId", "")
        if not order_id:
            return Response({"detail": "缺少订单号"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = DistributionOrder.objects.get(order_id=order_id)
        except DistributionOrder.DoesNotExist:
            return Response({"detail": "订单不存在"}, status=status.HTTP_404_NOT_FOUND)

        if order.status == "paid":
            return Response({"detail": "订单已支付", "orderId": order_id})

        order.status = "paid"
        order.paid_at = timezone.now()
        order.save()
        return Response(
            {"detail": "支付成功，体验包已开通", "orderId": order_id},
            status=status.HTTP_200_OK,
        )
