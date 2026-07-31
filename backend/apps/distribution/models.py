# -*- coding: utf-8 -*-
"""分销体系模型：推广员 / 推广海报 / 分销订单 / 佣金 / 提现 / 客户登记报表"""
from django.conf import settings
from django.db import models


class Promoter(models.Model):
    """推广员"""

    STATUS_CHOICES = (
        ("active", "正常"),
        ("frozen", "已冻结"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="promoter", verbose_name="关联用户",
    )
    name = models.CharField("推广昵称", max_length=64)
    invite_code = models.CharField("邀请码", max_length=32, unique=True)
    rate = models.DecimalField("返佣比例", max_digits=4, decimal_places=2, default="0.20")
    customers = models.IntegerField("推广人数", default=0)
    withdrawn_total = models.DecimalField("累计已提现", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="active")
    freeze_reason = models.CharField("冻结原因", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("申请时间", auto_now_add=True)

    class Meta:
        db_table = "dist_promoter"
        verbose_name = "推广员"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}({self.invite_code})"

    @property
    def total_commission(self):
        """累计佣金（含待结算）"""
        agg = self.commissions.aggregate(total=models.Sum("amount"))
        return agg["total"] or 0

    @property
    def withdrawable(self):
        """可提现（已结算 - 已提现）"""
        agg = self.commissions.filter(status="paid").aggregate(total=models.Sum("amount"))
        total = agg["total"] or 0
        return total - (self.withdrawn_total or 0)


class PromoPoster(models.Model):
    """推广海报（含 0.01 元体验包订单）"""

    promoter = models.ForeignKey(Promoter, on_delete=models.CASCADE, related_name="posters")
    title = models.CharField("海报标题", max_length=128, default="客户大数据平台")
    image_url = models.CharField("海报图片 URL", max_length=512, blank=True, default="")
    trial_price = models.DecimalField("体验包价格", max_digits=6, decimal_places=2, default="0.01")
    enabled = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "dist_poster"
        verbose_name = "推广海报"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.promoter.name} 的海报"


class DistributionOrder(models.Model):
    """分销订单（0.01 元体验包订单 / 升级套餐）"""

    STATUS_CHOICES = (
        ("pending", "待支付"),
        ("paid", "已支付"),
        ("refunded", "已退款"),
        ("closed", "已关闭"),
    )
    PAY_CHANNELS = (
        ("wechat", "微信支付"),
        ("alipay", "支付宝"),
    )

    order_id = models.CharField("订单号", max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="dist_orders", verbose_name="下单用户",
    )
    promoter = models.ForeignKey(
        Promoter, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="推广员",
    )
    plan_code = models.CharField("套餐编码", max_length=32, default="trial")
    amount = models.DecimalField("金额", max_digits=10, decimal_places=2)
    channel = models.CharField("支付渠道", max_length=16, choices=PAY_CHANNELS, default="wechat")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="pending")
    commission_amount = models.DecimalField("佣金金额", max_digits=12, decimal_places=4, default="0")
    commission_status = models.CharField(
        "佣金状态", max_length=16, default="pending",
        choices=(("pending", "待结算"), ("paid", "已结算"), ("cancelled", "已取消")),
    )
    created_at = models.DateTimeField("下单时间", auto_now_add=True)
    paid_at = models.DateTimeField("支付时间", null=True, blank=True)

    class Meta:
        db_table = "dist_order"
        verbose_name = "分销订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_id


class Commission(models.Model):
    """佣金记录"""

    STATUS_CHOICES = (
        ("pending", "待结算"),
        ("paid", "已结算"),
        ("cancelled", "已取消"),
    )

    promoter = models.ForeignKey(
        Promoter, on_delete=models.CASCADE, related_name="commissions", verbose_name="推广员",
    )
    order = models.ForeignKey(
        DistributionOrder, on_delete=models.CASCADE,
        related_name="commissions", verbose_name="来源订单",
    )
    amount = models.DecimalField("佣金金额", max_digits=12, decimal_places=4)
    rate = models.DecimalField("返佣比例", max_digits=4, decimal_places=2, default="0.20")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    settled_at = models.DateTimeField("结算时间", null=True, blank=True)

    class Meta:
        db_table = "dist_commission"
        verbose_name = "佣金记录"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.promoter.name} +{self.amount}"


class Withdrawal(models.Model):
    """提现申请"""

    STATUS_CHOICES = (
        ("pending", "待审核"),
        ("approved", "已打款"),
        ("rejected", "已驳回"),
    )
    CHANNEL_CHOICES = (
        ("wechat", "微信"),
        ("alipay", "支付宝"),
    )

    withdrawal_id = models.CharField("提现单号", max_length=64, unique=True)
    promoter = models.ForeignKey(
        Promoter, on_delete=models.CASCADE, related_name="withdrawals", verbose_name="推广员",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="withdrawals", verbose_name="用户",
    )
    amount = models.DecimalField("提现金额", max_digits=10, decimal_places=2)
    channel = models.CharField("收款渠道", max_length=16, choices=CHANNEL_CHOICES, default="wechat")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="pending")
    payout_id = models.CharField("分账流水号", max_length=64, blank=True, default="")
    remark = models.CharField("备注", max_length=255, blank=True, default="")
    request_time = models.DateTimeField("申请时间", auto_now_add=True)
    processed_time = models.DateTimeField("处理时间", null=True, blank=True)

    class Meta:
        db_table = "dist_withdrawal"
        verbose_name = "提现申请"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.withdrawal_id} {self.amount}"


class CustomerReport(models.Model):
    """客户登记报表（推广员 → 其推广的客户）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="customer_reports", verbose_name="客户用户",
    )
    promoter = models.ForeignKey(
        Promoter, on_delete=models.CASCADE, related_name="customer_reports", verbose_name="推广员",
    )
    identity_subject = models.CharField("实名主体", max_length=64, blank=True, default="")
    plan_status = models.CharField("套餐", max_length=32, blank=True, default="")
    customer_contact = models.CharField("联系方式", max_length=64, blank=True, default="")
    device_ip = models.GenericIPAddressField("注册 IP", null=True, blank=True)
    registration_time = models.DateTimeField("注册时间", auto_now_add=True)
    payment_channel = models.CharField("支付渠道", max_length=16, blank=True, default="")
    payment_history = models.IntegerField("支付次数", default=0)
    commission_history = models.IntegerField("佣金笔数", default=0)
    operation_logs = models.IntegerField("操作次数", default=0)

    class Meta:
        db_table = "dist_customer_report"
        verbose_name = "客户登记报表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.promoter.name} -> {self.user.username}"


def generate_order_id(prefix="ord"):
    """生成订单号：prefix + 毫秒时间戳"""
    import time
    return f"{prefix}_{int(time.time() * 1000)}"


def generate_withdrawal_id():
    import time
    return f"wd_{int(time.time() * 1000)}"


def generate_invite_code():
    """生成 6 位邀请码"""
    import random
    import string
    return "INV" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
