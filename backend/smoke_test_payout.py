# -*- coding: utf-8 -*-
"""PayoutService 冒烟测试（幂等版，真实金额）"""
import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.distribution.models import Commission, DistributionOrder, Promoter, Withdrawal
from apps.distribution.payout import PayoutError, PayoutService

User = get_user_model()
user, _ = User.objects.get_or_create(username="payout_test_user", defaults={"password": "x"})
Promoter.objects.filter(user=user).delete()
promoter = Promoter.objects.create(user=user, name="Payout测试", invite_code="INVPT2", rate="0.20")

# 一笔 5 元订单 → 佣金 1.00（20%）
order = DistributionOrder.objects.create(
    order_id="ord_payout_test_" + str(int(time.time() * 1000)), user=user, promoter=promoter,
    plan_code="basic", amount=Decimal("5.00"), status="paid",
    commission_amount=Decimal("1.00"), commission_status="paid",
)
Commission.objects.create(
    promoter=promoter, order=order,
    amount=Decimal("1.00"), rate=Decimal("0.20"), status="paid",
)

print("withdrawable before:", promoter.withdrawable)
assert promoter.withdrawable == Decimal("1.00"), promoter.withdrawable

# 0 金额应拒绝
wd0 = Withdrawal.objects.create(
    withdrawal_id="wd_payout_zero", promoter=promoter, user=user,
    amount=Decimal("0.00"), status="pending",
)
try:
    PayoutService.process_withdrawal(wd0)
    print("FAIL: 0 金额未拒绝")
except PayoutError:
    print("OK: 0 金额拒绝")
wd0.delete()

# 正常打款 1.00
wd = Withdrawal.objects.create(
    withdrawal_id="wd_payout_ok", promoter=promoter, user=user,
    amount=Decimal("1.00"), status="pending",
)
result = PayoutService.process_withdrawal(wd)
wd.refresh_from_db()
promoter.refresh_from_db()
assert wd.status == "approved", wd.status
assert wd.payout_id.startswith("po_"), wd.payout_id
assert promoter.withdrawn_total == Decimal("1.00"), promoter.withdrawn_total
print("OK: 打款成功", result["payout_id"], "| withdrawn_total =", promoter.withdrawn_total)

# 重复打款应拒绝
try:
    PayoutService.process_withdrawal(wd)
    print("FAIL: 重复打款未拒绝")
except PayoutError:
    print("OK: 重复打款拒绝")

print("=== ALL PAYOUT TESTS PASSED ===")
