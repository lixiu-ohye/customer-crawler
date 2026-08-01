"""商业化体系 models: 套餐/实名/额度/设备管控/行为日志/增值服务/优惠券"""
from django.conf import settings
from django.db import models


class PlanDefinition(models.Model):
    """套餐定义表（5 档）"""

    plan_code = models.CharField("套餐编码", max_length=32, unique=True)
    plan_name = models.CharField("套餐名", max_length=64)
    price_monthly = models.DecimalField("月价", max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField("年价", max_digits=10, decimal_places=2, default=0)

    # 采集
    concurrent_tasks = models.IntegerField("并发任务数", default=1)
    daily_leads = models.IntegerField("每日线索上限", default=30)
    crawl_min_interval_min = models.IntegerField("采集最小间隔(分)", default=15)
    crawling_speed = models.CharField("爬虫速度", max_length=16, default="slow")

    # AI
    daily_ai_summary = models.IntegerField("每日AI摘要", default=10)
    daily_ai_copy = models.IntegerField("每日AI话术", default=5)
    ai_monthly_total = models.IntegerField("月度AI总额", default=0)

    # 导出/词库
    export_single_limit = models.IntegerField("单次导出上限", default=50)
    export_async = models.BooleanField("异步导出", default=False)
    keyword_total_limit = models.IntegerField("关键词总上限", default=20)
    keyword_per_task = models.IntegerField("单任务词上限", default=10)

    # 功能
    monitoring_tasks = models.IntegerField("监控任务数(-1不限)", default=0)
    industry_templates = models.IntegerField("行业模板数(-1全部)", default=0)
    alert_channels = models.CharField("告警渠道", max_length=64, blank=True, default="")
    heatmap_level = models.CharField("热力图", max_length=16, default="none")
    sub_accounts = models.IntegerField("子账号数(-1不限)", default=0)
    lead_locking = models.BooleanField("线索锁定", default=False)
    lead_retention_days = models.IntegerField("线索保留天数", default=7)
    lead_masking = models.CharField("脱敏级别", max_length=16, default="light")
    regional_filter = models.BooleanField("区县地域过滤", default=False)
    data_reports = models.BooleanField("经营数据报表", default=False)
    operation_service = models.BooleanField("人工运营服务", default=False)
    permission_levels = models.BooleanField("权限分级", default=False)
    private_deployment = models.BooleanField("私有化部署", default=False)

    yearly_bonus = models.JSONField("年付福利", default=dict, blank=True)
    sort_order = models.IntegerField("排序", default=0)
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "plan_definition"
        verbose_name = "套餐定义"
        verbose_name_plural = verbose_name
        ordering = ("sort_order",)

    def __str__(self):
        return self.plan_name


class RealNameAuth(models.Model):
    """实名认证（一证一号 + 人脸核验）"""

    STATUS_CHOICES = (
        ("pending", "待核验"), ("verified", "已认证"), ("rejected", "已驳回"), ("banned", "已处罚"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="realname",
    )
    id_card_md5 = models.CharField("身份证MD5(一证一号)", max_length=32, unique=True)
    real_name = models.CharField("真实姓名", max_length=64)
    id_card_tail = models.CharField("身份证后4位", max_length=4, blank=True, default="")
    face_image_path = models.CharField("人脸照片", max_length=255, blank=True, default="")
    face_verified = models.BooleanField("人脸核验通过", default=False)
    verify_provider = models.CharField("核验服务商", max_length=32, blank=True, default="")
    license_image_path = models.CharField("营业执照", max_length=255, blank=True, default="")
    license_verified = models.BooleanField("执照核验", default=False)
    auth_status = models.CharField("认证状态", max_length=16, choices=STATUS_CHOICES, default="pending")
    ban_until = models.DateTimeField("禁实名至", null=True, blank=True)
    ban_reason = models.CharField("处罚原因", max_length=255, blank=True, default="")
    auth_date = models.DateTimeField("认证时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "real_name_auth"
        verbose_name = "实名认证"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.real_name}({self.get_auth_status_display()})"


class UserQuota(models.Model):
    """用户每日额度（每日 0 点统一重置）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quotas",
    )
    quota_date = models.DateField("额度日期")
    leads_used = models.IntegerField("已用线索", default=0)
    leads_limit = models.IntegerField("线索上限", default=30)
    ai_summary_used = models.IntegerField("已用摘要", default=0)
    ai_summary_limit = models.IntegerField("摘要上限", default=10)
    ai_copy_used = models.IntegerField("已用话术", default=0)
    ai_copy_limit = models.IntegerField("话术上限", default=5)
    export_used = models.IntegerField("已导出", default=0)
    export_limit = models.IntegerField("导出上限", default=50)
    is_demoted = models.BooleanField("静默降权", default=False)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "user_quota"
        verbose_name = "用户额度"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=["user", "quota_date"], name="uk_user_quota_date"),
        ]

    def __str__(self):
        return f"{self.user_id} {self.quota_date}"


class DeviceIpControl(models.Model):
    """设备/IP 管控（防批量注册）"""

    ACTION_CHOICES = (
        ("register", "注册"), ("login", "登录"), ("collect", "采集"),
    )

    ip_address = models.CharField("IP", max_length=45)
    device_id = models.CharField("设备ID", max_length=128)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="device_controls",
    )
    register_count = models.IntegerField("该IP注册数", default=0)
    action = models.CharField("动作", max_length=16, choices=ACTION_CHOICES, default="register")
    is_blocked = models.BooleanField("拦截", default=False)
    block_reason = models.CharField("拦截原因", max_length=255, blank=True, default="")
    frozen_until = models.DateTimeField("冻结至", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "device_ip_control"
        verbose_name = "设备IP管控"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=["ip_address"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self):
        return f"{self.ip_address}/{self.device_id}"


class UserBehaviorLog(models.Model):
    """用户行为日志（违规判定）"""

    ACTION_CHOICES = (
        ("create_task", "新建任务"), ("delete_task", "删除任务"), ("toggle_task", "启停任务"),
        ("export", "导出"), ("purchase", "购买"), ("realname", "实名"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="behavior_logs",
    )
    action_type = models.CharField("动作", max_length=32, choices=ACTION_CHOICES)
    action_detail = models.JSONField("详情", default=dict, blank=True)
    ip = models.CharField("IP", max_length=45, blank=True, default="")
    is_violation = models.BooleanField("是否违规", default=False)
    penalty = models.CharField("处罚", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "user_behavior_log"
        verbose_name = "行为日志"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["is_violation"]),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.action_type}"


class ServicePurchase(models.Model):
    """增值服务购买"""

    TYPE_CHOICES = (
        ("monthly", "月度订阅"), ("one_time", "一次性"), ("enterprise", "企业专属"),
    )
    STATUS_CHOICES = (
        ("active", "生效中"), ("expired", "已过期"), ("cancelled", "已取消"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_purchases",
    )
    service_code = models.CharField("服务编码", max_length=64)
    service_name = models.CharField("服务名", max_length=64)
    service_type = models.CharField("类型", max_length=16, choices=TYPE_CHOICES)
    price = models.DecimalField("价格", max_digits=10, decimal_places=2, default=0)
    bonus_value = models.IntegerField("赠量(条/天)", default=0)
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="active")
    start_date = models.DateTimeField("开始", auto_now_add=True)
    expiry_date = models.DateTimeField("到期", null=True, blank=True)

    class Meta:
        db_table = "service_purchase"
        verbose_name = "增值服务"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.service_name}({self.user_id})"


class Coupon(models.Model):
    """优惠券"""

    DISCOUNT_CHOICES = (
        ("fixed", "立减"), ("percent", "折扣"),
    )

    coupon_code = models.CharField("券码", max_length=64, unique=True)
    coupon_name = models.CharField("券名", max_length=64)
    discount_type = models.CharField("类型", max_length=16, choices=DISCOUNT_CHOICES, default="fixed")
    discount_value = models.DecimalField("面值", max_digits=10, decimal_places=2)
    min_amount = models.DecimalField("门槛", max_digits=10, decimal_places=2, default=0)
    cond_first_purchase = models.BooleanField("仅首充", default=False)
    cond_from_plan = models.CharField("从套餐", max_length=32, blank=True, default="")
    cond_to_plan = models.CharField("升到套餐", max_length=32, blank=True, default="")
    expiry_days = models.IntegerField("有效期(天)", default=30)
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "coupon"
        verbose_name = "优惠券"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.coupon_name


class UserCoupon(models.Model):
    """用户优惠券"""

    STATUS_CHOICES = (
        ("unused", "未使用"), ("used", "已使用"), ("expired", "已过期"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupons",
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="user_coupons")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="unused")
    used_at = models.DateTimeField("使用时间", null=True, blank=True)
    expiry_date = models.DateTimeField("过期时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "user_coupon"
        verbose_name = "用户优惠券"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=["user", "coupon"], name="uk_user_coupon"),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.coupon_id}"
