"""短视频评论截流链路 models: 监控目标/原始评论/意图评论/触发规则/话术模板/账号池"""
from django.conf import settings
from django.db import models


class MonitorTarget(models.Model):
    """监控目标池"""

    TARGET_CHOICES = (
        ("video", "视频"), ("live_room", "直播间"), ("competitor_account", "竞品账号"),
    )
    PLATFORM_CHOICES = (
        ("douyin", "抖音"), ("shipinhao", "视频号"), ("kuaishou", "快手"),
    )
    STATUS_CHOICES = (
        ("active", "监控中"), ("paused", "已暂停"), ("stopped", "已停止"),
    )

    target_type = models.CharField("目标类型", max_length=32, choices=TARGET_CHOICES)
    target_id = models.CharField("平台侧ID", max_length=64)
    platform = models.CharField("平台", max_length=16, choices=PLATFORM_CHOICES)
    title = models.CharField("标题", max_length=200, blank=True, default="")
    monitor_status = models.CharField("监控状态", max_length=16, choices=STATUS_CHOICES, default="active")
    last_pull_time = models.DateTimeField("上次拉取", null=True, blank=True)
    pull_interval_min = models.IntegerField("拉取间隔(分)", default=5)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="monitor_targets",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "monitor_target"
        verbose_name = "监控目标"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "target_type", "target_id"],
                name="uk_monitor_target",
            ),
        ]

    def __str__(self):
        return self.title or self.target_id


class RawComment(models.Model):
    """原始评论表（幂等入）"""

    PLATFORM_CHOICES = MonitorTarget.PLATFORM_CHOICES

    comment_id = models.CharField("平台评论ID", max_length=64)
    target = models.ForeignKey(MonitorTarget, on_delete=models.CASCADE, related_name="comments")
    platform = models.CharField("平台", max_length=16, choices=PLATFORM_CHOICES)
    uid = models.CharField("用户ID", max_length=64)
    nickname = models.CharField("昵称", max_length=100, blank=True, default="")
    avatar_url = models.URLField("头像", blank=True, default="")
    fan_cnt = models.IntegerField("粉丝数", default=0)
    region = models.CharField("地区", max_length=32, blank=True, default="")
    content = models.TextField("评论内容")
    like_count = models.IntegerField("点赞数", default=0)
    reply_count = models.IntegerField("回复数", default=0)
    parent_comment_id = models.CharField("父评论ID", max_length=64, blank=True, default="")
    comment_time = models.DateTimeField("评论时间", null=True, blank=True)
    pulled_at = models.DateTimeField("拉取时间", auto_now_add=True)

    class Meta:
        db_table = "raw_comment"
        verbose_name = "原始评论"
        verbose_name_plural = verbose_name
        ordering = ("-pulled_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "comment_id"],
                name="uk_raw_comment",
            ),
        ]
        indexes = [
            models.Index(fields=["target"]),
            models.Index(fields=["uid"]),
        ]

    def __str__(self):
        return f"{self.nickname}: {self.content[:30]}"


class IntentComment(models.Model):
    """意图识别结果"""

    LEVEL_CHOICES = (
        ("kw_only", "关键词命中"), ("nlp_pass", "NLP通过"), ("llm_pass", "LLM通过"),
    )

    raw_comment = models.ForeignKey(RawComment, on_delete=models.CASCADE, related_name="intent")
    intent_score = models.DecimalField("意图分", max_digits=4, decimal_places=2, default=0)
    hit_keyword = models.CharField("命中词", max_length=64, blank=True, default="")
    level = models.CharField("识别级别", max_length=16, choices=LEVEL_CHOICES, default="kw_only")
    is_ad = models.BooleanField("广告/同行/已转化", default=False)
    is_converted = models.BooleanField("已转化", default=False)
    llm_raw = models.JSONField("LLM原始结果", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "intent_comment"
        verbose_name = "意图评论"
        verbose_name_plural = verbose_name
        ordering = ("-intent_score",)
        indexes = [
            models.Index(fields=["intent_score"]),
            models.Index(fields=["is_converted"]),
        ]

    def __str__(self):
        return f"{self.intent_score:.2f} {self.raw_comment_id}"


class TriggerRule(models.Model):
    """动作引擎规则"""

    ACTION_CHOICES = (
        ("send_dm", "发私信"), ("reply_comment", "回评"), ("push_card", "推名片"),
    )

    name = models.CharField("规则名", max_length=64)
    cond_intent_min = models.DecimalField("意图分阈值", max_digits=4, decimal_places=2, default=0.70)
    cond_fan_min = models.IntegerField("粉丝下限", default=50)
    cond_fan_max = models.IntegerField("粉丝上限", default=5000)
    cond_exclude_following = models.BooleanField("排除互关", default=True)
    action_type = models.CharField("动作类型", max_length=16, choices=ACTION_CHOICES)
    template = models.ForeignKey(
        "DmTemplate", on_delete=models.SET_NULL, null=True, blank=True, related_name="rules",
    )
    round = models.IntegerField("触达轮次", default=1)
    enabled = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "trigger_rule"
        verbose_name = "触发规则"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DmTemplate(models.Model):
    """私信话术模板（三轮触达）"""

    MEDIA_CHOICES = (
        ("text", "文本"), ("card", "名片"), ("qrcode", "二维码"),
    )

    name = models.CharField("模板名", max_length=64)
    round = models.IntegerField("轮次", default=1)
    content = models.TextField("话术内容")
    media_type = models.CharField("素材类型", max_length=16, choices=MEDIA_CHOICES, default="text")
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "dm_template"
        verbose_name = "话术模板"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AccountPool(models.Model):
    """多账号资源池（Cookie 健康度 + 频控）"""

    PLATFORM_CHOICES = MonitorTarget.PLATFORM_CHOICES
    STATUS_CHOICES = (
        ("active", "可用"), ("frozen", "冻结"), ("cooling", "冷却"),
    )

    platform = models.CharField("平台", max_length=16, choices=PLATFORM_CHOICES)
    account_name = models.CharField("账号名", max_length=64)
    cookie_encrypted = models.TextField("Cookie密文", blank=True, default="")
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="active")
    health_score = models.DecimalField("健康度", max_digits=4, decimal_places=2, default=1.00)
    today_sent = models.IntegerField("今日已发", default=0)
    hourly_sent = models.IntegerField("本时已发", default=0)
    last_sent_at = models.DateTimeField("最后发送", null=True, blank=True)
    last_error = models.CharField("最后错误", max_length=200, blank=True, default="")
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "account_pool"
        verbose_name = "账号池"
        verbose_name_plural = verbose_name
        ordering = ("-health_score",)

    def __str__(self):
        return f"{self.account_name}({self.get_platform_display()})"
