# -*- coding: utf-8 -*-
"""分账打款服务（真实分账 API 对接层）

对接第三方支付托管（云购OS / MallBook / 拉卡拉银行托管）的分账打款：
- 审核通过后调用真实打款接口
- 生成 payout_id 留痕
- 累计 promoter.withdrawn_total（可提现余额 = 已结算佣金 - 已提现金额）
- 写 UserBehaviorLog 审计

本文件为适配层：第三方 SDK 需替换为真实商户密钥对接。
"""
import time

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.commerce.models import UserBehaviorLog


class PayoutError(Exception):
    """打款失败"""


class PayoutService:
    """提现打款服务（模拟第三方资金托管分账）"""

    # 第三方托管平台（可配置）
    PROVIDER = "yungouos"  # 云购OS 资金托管

    @classmethod
    def _call_provider(cls, withdrawal):
        """调用第三方托管打款接口（模拟实现，返回支付流水号）

        生产环境：替换为真实 API 调用，例如
        yungouApi.splitOrder(withdrawal.withdrawal_id, amount=withdrawal.amount, account=...)
        并校验签名/幂等（同 withdrawal_id 不可重复打款）。
        """
        return {
            "payout_id": f"po_{int(time.time() * 1000)}",
            "provider": cls.PROVIDER,
            "amount": str(withdrawal.amount),
            "channel": withdrawal.channel,
            "status": "success",
            "paid_at": timezone.now().isoformat(),
        }

    @classmethod
    @transaction.atomic
    def process_withdrawal(cls, withdrawal):
        """处理提现打款：调用第三方 + 更新状态 + 扣减可提现余额 + 审计"""
        if withdrawal.status != "pending":
            raise PayoutError(f"提现状态不是待审核: {withdrawal.status}")
        if withdrawal.amount <= 0:
            raise PayoutError("提现金额必须大于 0")

        promoter = withdrawal.promoter

        # 1. 调用第三方托管打款
        result = cls._call_provider(withdrawal)

        # 2. 更新提现状态
        withdrawal.status = "approved"
        withdrawal.payout_id = result["payout_id"]
        withdrawal.processed_time = timezone.now()
        withdrawal.remark = f"分账打款成功（{cls.PROVIDER}）"
        withdrawal.save(update_fields=["status", "payout_id", "processed_time", "remark"])

        # 3. 累计已提现（可提现余额 = 已结算佣金 - 已提现）
        promoter.withdrawn_total = Decimal(promoter.withdrawn_total or 0) + withdrawal.amount
        promoter.save(update_fields=["withdrawn_total"])

        # 4. 审计留痕
        UserBehaviorLog.objects.create(
            user=withdrawal.user,
            action_type="withdrawal_payout",
            action_detail={
                "withdrawal_id": withdrawal.withdrawal_id,
                "payout_id": result["payout_id"],
                "amount": str(withdrawal.amount),
                "provider": cls.PROVIDER,
            },
        )
        return result
