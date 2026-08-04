# -*- coding: utf-8 -*-
"""线索模型"""
from django.conf import settings
from django.db import models


class Lead(models.Model):
    """客户线索"""

    PLATFORM_CHOICES = (
        ("douyin", "抖音"), ("xiaohongshu", "小红书"), ("kuaishou", "快手"),
        ("weibo", "微博"), ("zhihu", "知乎"), ("tieba", "贴吧"),
    )
    INTENT_CHOICES = (
        ("high", "高意向"), ("medium", "中意向"), ("low", "低意向"), ("none", "无意向"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leads")
    task_id = models.CharField("任务ID", max_length=32, blank=True, default="")
    platform = models.CharField("平台", max_length=24, choices=PLATFORM_CHOICES)
    item_id = models.CharField("平台内容ID", max_length=64, blank=True, default="")
    title = models.CharField("标题", max_length=200, blank=True, default="")
    content = models.TextField("正文")
    author = models.CharField("作者", max_length=100, blank=True, default="")
    author_id = models.CharField("作者ID", max_length=64, blank=True, default="")
    url = models.URLField("原文链接", blank=True, default="")
    like_count = models.IntegerField("点赞", default=0)
    comment_count = models.IntegerField("评论", default=0)
    share_count = models.IntegerField("分享", default=0)
    publish_time = models.DateTimeField("发布时间", null=True, blank=True)
    region = models.CharField("地域标签", max_length=50, blank=True, default="")
    demand = models.CharField("需求标签", max_length=50, blank=True, default="")
    intent_label = models.CharField("意向等级", max_length=16, choices=INTENT_CHOICES, default="none")
    intent_score = models.IntegerField("意向分", default=0)
    score_breakdown = models.JSONField("打分明细", default=dict, blank=True)
    tags = models.JSONField("标签", default=list, blank=True)
    lng = models.FloatField("经度", null=True, blank=True)
    lat = models.FloatField("纬度", null=True, blank=True)
    location_text = models.CharField("地址文本", max_length=200, blank=True, default="")
    is_customer = models.BooleanField("是否客户", default=None, null=True, blank=True)
    customer_type = models.CharField("客户类型", max_length=16, blank=True, default="")
    customer_reason = models.CharField("客户判定理由", max_length=200, blank=True, default="")
    contact_hint = models.CharField("联系方式线索", max_length=50, blank=True, default="")
    needs = models.CharField("客户需求", max_length=200, blank=True, default="")
    status = models.CharField("状态", max_length=16, default="new")
    note = models.TextField("备注", blank=True, default="")
    is_favorite = models.BooleanField("收藏", default=False)
    is_blacklisted = models.BooleanField("拉黑", default=False)
    created_at = models.DateTimeField("入库时间", auto_now_add=True)

    class Meta:
        db_table = "lead"
        verbose_name = "线索"
        verbose_name_plural = verbose_name
        ordering = ("-intent_score", "-id")
        indexes = [
            models.Index(fields=["user", "platform"]),
            models.Index(fields=["user", "intent_score"]),
            models.Index(fields=["user", "region"]),
        ]

    def __str__(self):
        return f"{self.platform}:{self.title[:20]}"
