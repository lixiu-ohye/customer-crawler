"""CRM 公海池 models: 线索流转/导出审计"""
from django.conf import settings
from django.db import models


class LeadPool(models.Model):
    """线索公海池（销售流转核心）"""

    STATUS_CHOICES = (
        ("unclaimed", "未领取"), ("claimed", "已领取"), ("following", "跟进中"),
        ("converted", "已成交"), ("recycled", "已回收"),
    )

    lead = models.ForeignKey(
        "leads.Lead", on_delete=models.CASCADE, null=True, blank=True, related_name="pool_records",
    )
    company = models.ForeignKey(
        "biz.Company", on_delete=models.CASCADE, null=True, blank=True, related_name="pool_records",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pool_records", verbose_name="领取人",
    )
    status = models.CharField("状态", max_length=16, choices=STATUS_CHOICES, default="unclaimed")
    claimed_at = models.DateTimeField("领取时间", null=True, blank=True)
    last_follow_at = models.DateTimeField("最后跟进", null=True, blank=True)
    recycle_days = models.IntegerField("回收天数", default=7)
    follow_notes = models.JSONField("跟进记录", default=list, blank=True)
    converted_at = models.DateTimeField("成交时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "crm_lead_pool"
        verbose_name = "线索公海池"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["status", "last_follow_at"]),
        ]

    def __str__(self):
        return f"pool#{self.id}({self.get_status_display()})"


class ExportAuditLog(models.Model):
    """导出审计日志（合规红线：扣点/水印/留痕）"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="export_logs",
    )
    company_count = models.IntegerField("企业数", default=0)
    has_phone = models.BooleanField("含手机号", default=False)
    purpose = models.CharField("用途声明", max_length=100, blank=True, default="")
    watermark = models.CharField("水印", max_length=64, blank=True, default="")
    cost_points = models.IntegerField("扣点数", default=0)
    ip = models.CharField("IP", max_length=45, blank=True, default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "export_audit_log"
        verbose_name = "导出审计"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"export#{self.id}({self.company_count}家)"
