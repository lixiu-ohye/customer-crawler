"""分销体系 API：推广员 / 海报 / 0.01 元体验包注册 / 佣金 / 提现 / 开发者后台"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.commerce.models import ServicePurchase, UserBehaviorLog
from apps.distribution.payout import PayoutError, PayoutService
from apps.distribution.models import (
    Commission,
    CustomerReport,
    DistributionOrder,
    Promoter,
    PromoPoster,
    Withdrawal,
    generate_invite_code,
    generate_order_id,
    generate_withdrawal_id,
)
from apps.users.models import User


class PromoterMyView(APIView):
    """我的推广信息（推广员状态 + 统计）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            promoter = request.user.promoter
        except Promoter.DoesNotExist:
            return Response({"promoter": None, "stats": {}})

        return Response({
            "promoter": {
                "id": promoter.id,
                "name": promoter.name,
                "invite_code": promoter.invite_code,
                "rate": str(promoter.rate),
                "customers": promoter.customers,
                "status": promoter.status,
                "freeze_reason": promoter.freeze_reason,
            },
            "stats": {
                "total_commission": str(promoter.total_commission),
                "withdrawable": str(promoter.withdrawable),
                "customers": promoter.customers,
            },
        })


class PromoterApplyView(APIView):
    """申请成为推广员"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        name = request.data.get("name", "").strip()
        if len(name) < 2:
            return Response({"detail": "推广昵称至少 2 个字符"}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(request.user, "promoter"):
            return Response({"detail": "您已是推广员"}, status=status.HTTP_400_BAD_REQUEST)

        # 邀请码唯一性
        invite_code = generate_invite_code()
        while Promoter.objects.filter(invite_code=invite_code).exists():
            invite_code = generate_invite_code()

        promoter = Promoter.objects.create(
            user=request.user, name=name, invite_code=invite_code, rate=Decimal("0.20"),
        )
        PromoPoster.objects.create(promoter=promoter, title="客户大数据平台")
        UserBehaviorLog.objects.create(
            user=request.user, action_type="promoter_apply",
            action_detail={"invite_code": invite_code},
        )
        return Response(
            {"detail": "申请成功，已生成邀请码 " + invite_code,
             "promoter": {"id": promoter.id, "name": name, "invite_code": invite_code, "rate": "0.20"}},
            status=status.HTTP_201_CREATED,
        )


class PromoterCommissionsView(APIView):
    """我的佣金明细"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            promoter = request.user.promoter
        except Promoter.DoesNotExist:
            return Response({"results": [], "total": 0})

        rows = []
        for c in promoter.commissions.select_related("order").all():
            rows.append({
                "order_id": c.order.order_id,
                "amount": str(c.amount),
                "rate": str(c.rate),
                "status": c.status,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return Response({"results": rows, "total": len(rows)})


class PromoterWithdrawView(APIView):
    """申请提现"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            promoter = request.user.promoter
        except Promoter.DoesNotExist:
            return Response({"detail": "请先申请成为推广员"}, status=status.HTTP_400_BAD_REQUEST)

        if promoter.status == "frozen":
            return Response({"detail": "推广员已被冻结，无法提现"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(request.data.get("amount", "0")))
        except Exception:
            return Response({"detail": "金额格式错误"}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"detail": "提现金额必须大于 0"}, status=status.HTTP_400_BAD_REQUEST)
        if amount > promoter.withdrawable:
            return Response({"detail": "可提现金额不足"}, status=status.HTTP_400_BAD_REQUEST)

        channel = request.data.get("channel", "wechat")
        if channel not in ("wechat", "alipay"):
            channel = "wechat"

        wd = Withdrawal.objects.create(
            withdrawal_id=generate_withdrawal_id(),
            promoter=promoter,
            user=request.user,
            amount=amount,
            channel=channel,
        )
        return Response(
            {"detail": "提现申请已提交，待审核", "withdrawalId": wd.withdrawal_id},
            status=status.HTTP_201_CREATED,
        )


class PromoterRegisterView(APIView):
    """0.01 元体验包注册（经推广海报 / 悬浮气泡进入）"""

    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        promoter_ref = request.data.get("promoter", "").strip()
        if not promoter_ref:
            return Response({"detail": "缺少推广信息（请通过推广海报注册）"}, status=status.HTTP_400_BAD_REQUEST)

        promoter = Promoter.objects.filter(
            invite_code__iexact=promoter_ref
        ).first()
        if not promoter:
            promoter = Promoter.objects.filter(name=promoter_ref).first()
        if not promoter:
            return Response({"detail": "无效的推广海报"}, status=status.HTTP_400_BAD_REQUEST)
        if promoter.status == "frozen":
            return Response({"detail": "该推广员已被冻结"}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        email = request.data.get("email", "").strip()
        if not username or len(password) < 6:
            return Response({"detail": "用户名必填，密码至少 6 位"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"detail": "用户名已存在"}, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户（trial 套餐）
        user = User(username=username, email=email, plan="trial", quota_limit=30)
        user.set_password(password)
        user.save()

        # 创建 0.01 元体验订单
        order = DistributionOrder.objects.create(
            order_id=generate_order_id(),
            user=user,
            promoter=promoter,
            plan_code="trial",
            amount=Decimal("0.01"),
            channel=request.data.get("channel", "wechat"),
            status="paid",
            paid_at=timezone.now(),
        )

        # 佣金（0.01 元，比例计算）
        commission_amount = (order.amount * promoter.rate).quantize(Decimal("0.0001"))
        Commission.objects.create(
            promoter=promoter, order=order,
            amount=commission_amount, rate=promoter.rate,
            status="paid", settled_at=timezone.now(),
        )
        order.commission_amount = commission_amount
        order.commission_status = "paid"
        order.save(update_fields=["commission_amount", "commission_status"])

        # 客户登记报表
        CustomerReport.objects.create(
            user=user, promoter=promoter,
            plan_status="trial",
            payment_channel=order.channel,
            payment_history=1,
            commission_history=1,
        )
        promoter.customers += 1
        promoter.save(update_fields=["customers"])

        from apps.users.middleware import create_token
        token = create_token(user)
        return Response(
            {
                "success": True,
                "message": "注册成功，已开通 0.01 元体验包",
                "orderId": order.order_id,
                "token": token,
                "user": {"id": user.id, "username": user.username, "plan": "trial"},
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# 开发者总后台（仅管理员 / 开发者）
# ---------------------------------------------------------------------------

def _require_dev(request):
    user = request.user
    if not (user.is_authenticated and (user.is_admin or user.is_developer_active)):
        return Response({"detail": "无开发者权限"}, status=status.HTTP_403_FORBIDDEN)
    return None


class AdminPlatformView(APIView):
    """开发者总后台：全量数据汇总"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        denied = _require_dev(request)
        if denied:
            return denied

        promoters = list(Promoter.objects.all().order_by("id"))
        orders = list(
            DistributionOrder.objects.select_related("user", "promoter").order_by("-created_at")[:100]
        )
        withdrawals = list(
            Withdrawal.objects.select_related("promoter", "user").order_by("-request_time")[:100]
        )
        reports = list(
            CustomerReport.objects.select_related("user", "promoter").order_by("-registration_time")[:100]
        )
        users = list(
            User.objects.order_by("id")[:200]
        )
        # 财务汇总
        paid_total = sum((o.amount for o in orders if o.status == "paid"), Decimal("0"))
        refund_total = sum((o.amount for o in orders if o.status == "refunded"), Decimal("0"))
        commission_total = sum(
            (o.commission_amount for o in orders if o.commission_status == "paid"),
            Decimal("0"),
        )
        wechat_paid = sum(
            (o.amount for o in orders if o.channel == "wechat" and o.status == "paid"),
            Decimal("0"),
        )
        alipay_paid = sum(
            (o.amount for o in orders if o.channel == "alipay" and o.status == "paid"),
            Decimal("0"),
        )
        wechat_refund = sum(
            (o.amount for o in orders if o.channel == "wechat" and o.status == "refunded"),
            Decimal("0"),
        )
        alipay_refund = sum(
            (o.amount for o in orders if o.channel == "alipay" and o.status == "refunded"),
            Decimal("0"),
        )

        return Response({
            "users": [
                {
                    "id": u.id, "username": u.username,
                    "plan": u.plan,
                    "identity": getattr(getattr(u, "realname", None), "auth_status", "none"),
                    "contact": u.phone or u.email,
                    "device_ip": "",
                    "registered_at": u.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_promoter": hasattr(u, "promoter"),
                }
                for u in users
            ],
            "orders": [
                {
                    "id": o.order_id, "user": o.user.username,
                    "plan": o.plan_code, "amount": str(o.amount),
                    "channel": o.channel, "status": o.status,
                    "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for o in orders
            ],
            "commissions": {
                p.name: [
                    {
                        "order_id": c.order.order_id, "amount": str(c.amount),
                        "rate": str(c.rate), "status": c.status,
                        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    for c in p.commissions.select_related("order").all()
                ]
                for p in promoters
            },
            "withdrawals": [
                {
                    "id": w.withdrawal_id, "user": w.user.username,
                    "amount": str(w.amount), "channel": w.channel,
                    "status": w.status,
                    "request_time": w.request_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for w in withdrawals
            ],
            "promoters": [
                {
                    "id": p.id, "name": p.name, "invite_code": p.invite_code,
                    "rate": str(p.rate), "customers": p.customers,
                    "status": p.status, "freeze_reason": p.freeze_reason,
                }
                for p in promoters
            ],
            "userReports": [
                {
                    "userId": r.user.username, "promoter": r.promoter.name,
                    "identitySubject": r.identity_subject,
                    "planStatus": r.plan_status,
                    "customerContact": r.customer_contact,
                    "deviceIP": r.device_ip or "",
                    "registrationTime": r.registration_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "paymentChannel": r.payment_channel,
                    "paymentHistory": r.payment_history,
                    "commissionHistory": r.commission_history,
                    "operationLogs": r.operation_logs,
                }
                for r in reports
            ],
            "financeReports": {
                "totalIncome": str(paid_total),
                "channelAgentFeeIncome": "0",
                "commissionExpense": str(commission_total),
                "wechatAlipayReconciliation": {
                    "wechat": {
                        "paid": str(wechat_paid),
                        "refunded": str(wechat_refund),
                        "balance": str(wechat_paid - wechat_refund),
                    },
                    "alipay": {
                        "paid": str(alipay_paid),
                        "refunded": str(alipay_refund),
                        "balance": str(alipay_paid - alipay_refund),
                    },
                },
                "reportDate": timezone.localdate().isoformat(),
            },
        })


class AdminPromoterFreezeView(APIView):
    """冻结 / 解冻推广员"""

    permission_classes = [IsAuthenticated]

    def post(self, request, promoter_id):
        denied = _require_dev(request)
        if denied:
            return denied

        try:
            promoter = Promoter.objects.get(id=promoter_id)
        except Promoter.DoesNotExist:
            return Response({"detail": "推广员不存在"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action", "freeze")
        if action == "freeze":
            promoter.status = "frozen"
            promoter.freeze_reason = request.data.get("reason", "违规操作")
        else:
            promoter.status = "active"
            promoter.freeze_reason = ""
        promoter.save(update_fields=["status", "freeze_reason"])
        return Response({"detail": "推广员已冻结：" + promoter.name if action == "freeze" else "推广员已解冻：" + promoter.name})


class AdminWithdrawalsView(APIView):
    """提现列表（开发者）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        denied = _require_dev(request)
        if denied:
            return denied
        qs = Withdrawal.objects.select_related("promoter", "user").order_by("-request_time")
        return Response({
            "results": [
                {
                    "id": w.withdrawal_id, "user": w.user.username,
                    "amount": str(w.amount), "channel": w.channel,
                    "status": w.status,
                    "request_time": w.request_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for w in qs
            ]
        })


class AdminWithdrawalProcessView(APIView):
    """审核提现（通过 / 驳回）"""

    permission_classes = [IsAuthenticated]

    def post(self, request, withdrawal_id):
        denied = _require_dev(request)
        if denied:
            return denied

        try:
            wd = Withdrawal.objects.get(withdrawal_id=withdrawal_id)
        except Withdrawal.DoesNotExist:
            return Response({"detail": "提现不存在"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status", "approved")
        if new_status not in ("approved", "rejected"):
            return Response({"detail": "无效状态"}, status=status.HTTP_400_BAD_REQUEST)

        # ?核：通? → 调?分?打款服务（第三方资金托管）；?回 → 直接更新状态
        if new_status == "approved":
            try:
                result = PayoutService.process_withdrawal(wd)
                return Response({
                    "detail": "已打款",
                    "payout_id": result.get("payout_id", ""),
                    "provider": result.get("provider", ""),
                })
            except PayoutError as exc:
                return Response({"detail": "打款失败: " + str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        wd.status = new_status
        wd.processed_time = timezone.now()
        wd.remark = request.data.get("remark", "")
        wd.save(update_fields=["status", "processed_time", "remark"])
        return Response({"detail": "已更新：" + new_status})
