"""B2B 企业线索链路 models: 企业主表/事件表/联系人/筛选模板"""
from django.conf import settings
from django.db import models


class Company(models.Model):
    """企业主表（维度表）"""

    STATUS_CHOICES = (
        ("active", "在业"), ("deregistered", "注销"), ("revoked", "吊销"),
    )
    CHANNEL_CHOICES = (
        ("factory", "工厂"), ("shop", "网店"), ("dealer", "经销商"),
    )

    name = models.CharField("企业名称", max_length=200)
    credit_code = models.CharField("统一社会信用代码", max_length=18, blank=True, default="")
    legal_person = models.CharField("法定代表人", max_length=64, blank=True, default="")
    reg_date = models.DateField("成立日期", null=True, blank=True)
    capital = models.DecimalField("注册资本(万)", max_digits=18, decimal_places=2, null=True, blank=True)
    status = models.CharField("经营状态", max_length=16, choices=STATUS_CHOICES, default="active")
    province = models.CharField("省", max_length=32, blank=True, default="")
    city = models.CharField("市", max_length=32, blank=True, default="")
    district = models.CharField("区县", max_length=32, blank=True, default="")
    industry_l3 = models.CharField("三级行业", max_length=64, blank=True, default="")
    product_tags = models.JSONField("业务标签", default=list, blank=True)
    channel_type = models.CharField("渠道类型", max_length=16, choices=CHANNEL_CHOICES, default="factory")

    # 规模信号
    insured_count = models.IntegerField("参保人数", default=0)
    recruit_cnt_30d = models.IntegerField("近30天招聘数", default=0)
    tender_cnt_90d = models.IntegerField("近90天招标数", default=0)
    patent_cnt = models.IntegerField("专利数", default=0)

    # 新鲜度
    last_tender_date = models.DateField("最近招标日", null=True, blank=True)
    last_recruit_date = models.DateField("最近招聘日", null=True, blank=True)
    last_financing_date = models.DateField("最近融资日", null=True, blank=True)

    # 地理
    lng = models.FloatField("经度", null=True, blank=True)
    lat = models.FloatField("纬度", null=True, blank=True)

    # 意向评分
    intent_score = models.IntegerField("意向分", default=0)

    data_version = models.IntegerField("数据版本", default=1)
    is_deleted = models.BooleanField("删除标记", default=False)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "dim_company"
        verbose_name = "企业"
        verbose_name_plural = verbose_name
        ordering = ("-intent_score", "-id")
        indexes = [
            models.Index(fields=["city", "industry_l3"]),
            models.Index(fields=["insured_count", "recruit_cnt_30d", "tender_cnt_90d"]),
            models.Index(fields=["reg_date"]),
        ]

    def __str__(self):
        return self.name


class CompanyEvent(models.Model):
    """企业动态事件表（事实表）"""

    EVENT_CHOICES = (
        ("tender", "招标"), ("financing", "融资"), ("recruit", "招聘"),
        ("lawsuit", "诉讼"), ("new_branch", "新设分支"),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField("事件类型", max_length=16, choices=EVENT_CHOICES)
    event_date = models.DateField("事件日期")
    event_detail = models.JSONField("事件详情", default=dict, blank=True)
    source_url = models.URLField("来源URL", blank=True, default="")
    source_platform = models.CharField("来源平台", max_length=32, blank=True, default="")
    is_valid = models.BooleanField("有效", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "fact_company_event"
        verbose_name = "企业事件"
        verbose_name_plural = verbose_name
        ordering = ("-event_date",)
        indexes = [
            models.Index(fields=["company", "event_date"]),
            models.Index(fields=["event_type", "event_date"]),
        ]

    def __str__(self):
        return f"{self.company.name}:{self.get_event_type_display()}"


class Contact(models.Model):
    """企业联系人表（决策人管线）"""

    VALID_CHOICES = (
        ("unknown", "未知"), ("valid", "有效"), ("empty", "空号"), ("stopped", "停机"),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField("姓名", max_length=64, blank=True, default="")
    phone = models.CharField("手机号(脱敏)", max_length=11, blank=True, default="")
    phone_md5 = models.CharField("手机号MD5", max_length=32, blank=True, default="")
    role_title = models.CharField("职位", max_length=64, blank=True, default="")
    role_score = models.DecimalField("决策人评分", max_digits=4, decimal_places=2, default=0)
    source_weight = models.DecimalField("来源权重", max_digits=4, decimal_places=2, default=0)
    source_list = models.JSONField("多源命中", default=list, blank=True)
    valid_status = models.CharField("号码状态", max_length=16, choices=VALID_CHOICES, default="unknown")
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="claimed_contacts", verbose_name="领取人",
    )
    claimed_at = models.DateTimeField("领取时间", null=True, blank=True)
    audit_log = models.JSONField("审计日志", default=list, blank=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "dim_contact"
        verbose_name = "联系人"
        verbose_name_plural = verbose_name
        ordering = ("-role_score", "-id")
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["role_score"]),
        ]

    def __str__(self):
        return f"{self.name}({self.role_title})"


class ScreenTemplate(models.Model):
    """高意向筛选模板（快启 69 行业模板思路）"""

    name = models.CharField("模板名", max_length=64)
    industry = models.CharField("行业", max_length=64, blank=True, default="")
    conditions = models.JSONField("条件快照", default=dict)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="screen_templates",
    )
    is_public = models.BooleanField("公共模板", default=False)
    usage_count = models.IntegerField("使用次数", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "screen_template"
        verbose_name = "筛选模板"
        verbose_name_plural = verbose_name
        ordering = ("-usage_count", "-id")

    def __str__(self):
        return self.name
