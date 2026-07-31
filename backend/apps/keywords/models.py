"""关键词模型"""
from django.conf import settings
from django.db import models


class KeywordGroup(models.Model):
    """关键词分组"""

    name = models.CharField("分组名", max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="keyword_groups")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "kw_group"
        verbose_name = "关键词分组"
        verbose_name_plural = verbose_name
        unique_together = ("name", "user")


class Keyword(models.Model):
    """关键词"""

    word = models.CharField("关键词", max_length=128)
    group = models.ForeignKey(KeywordGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="keywords")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="keywords")
    negative_words = models.TextField("否定词（逗号分隔）", blank=True, default="")
    hot_score = models.IntegerField("热度", default=0)
    enabled = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "kw_keyword"
        verbose_name = "关键词"
        verbose_name_plural = verbose_name
        unique_together = ("word", "user")
        ordering = ("-hot_score", "-id")

    def __str__(self):
        return self.word


class PromoterIndustry(models.Model):
    """推广员关注行业"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="promoter_industries")
    industry_id = models.IntegerField("行业ID")
    industry_name = models.CharField("行业名", max_length=64)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "promoter_industries"
        verbose_name = "推广员关注行业"
        verbose_name_plural = verbose_name
        unique_together = ("user", "industry_id")

    def __str__(self):
        return f"{self.user_id}-{self.industry_name}"
