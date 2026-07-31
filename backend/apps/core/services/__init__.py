"""合规服务：操作日志、采集日志、30 天数据自动清理、免责声明"""
import logging
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

# 合规免责声明全文
DISCLAIMER_TEXT = """
本平台提供的客户大数据采集与分析服务，旨在帮助用户合法合规地开展市场调研与客户开发工作。
使用本平台前，请您仔细阅读并理解以下条款：

一、合法性声明
1. 本平台采集的数据来源于互联网公开信息，仅限用于合法的商业调研、客户服务与市场分析用途。
2. 用户承诺：不得将本平台数据用于骚扰、诈骗、侵犯个人隐私、不正当竞争或其他任何违法违规活动。
3. 涉及个人信息的数据，用户应遵守《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》
   及《中华人民共和国网络安全法》等相关法律法规。

二、使用限制
1. 禁止利用本平台对任何平台进行恶意攻击、高频抓取、绕过风控等破坏性行为。
2. 禁止将线索数据出售、转售或提供给任何第三方用于非法用途。
3. 用户应合理控制采集频率，尊重各平台的服务协议与 robots 协议。

三、数据合规
1. 本平台对采集的数据执行 30 天自动清理机制，到期数据将自动删除。
2. 本平台记录全部操作日志与采集日志，留存备查。
3. 用户应对自身账号下的所有操作行为负责。

四、免责声明
1. 因用户违规使用本平台导致的法律责任，由用户自行承担。
2. 本平台不保证数据的完整性、准确性或时效性，数据仅供参考。
3. 本平台不对因使用数据产生的任何直接或间接损失承担责任。

五、其他
1. 本声明解释权归本平台所有，平台有权根据法律法规变化适时更新本声明。
2. 继续使用本平台即视为您已阅读并同意本声明的全部内容。
"""


class OperationLog(models.Model):
    """操作日志"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="op_logs"
    )
    action = models.CharField("操作", max_length=128)
    detail = models.TextField("详情", blank=True, default="")
    ip = models.GenericIPAddressField("IP", null=True, blank=True)
    created_at = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        db_table = "log_operation"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ("-id",)


class CrawlLog(models.Model):
    """采集日志"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="crawl_logs"
    )
    task_id = models.CharField("任务ID", max_length=32, blank=True, default="")
    platform = models.CharField("平台", max_length=24, blank=True, default="")
    keyword = models.CharField("关键词", max_length=128, blank=True, default="")
    status = models.CharField("状态", max_length=16, default="ok")
    detail = models.TextField("详情", blank=True, default="")
    created_at = models.DateTimeField("时间", auto_now_add=True)

    class Meta:
        db_table = "log_crawl"
        verbose_name = "采集日志"
        verbose_name_plural = verbose_name
        ordering = ("-id",)


def log_operation(user, action, detail="", ip=""):
    try:
        OperationLog.objects.create(user=user, action=action, detail=str(detail)[:500], ip=ip)
    except Exception:
        logger.exception("log_operation failed")


def log_crawl(user, task_id="", platform="", keyword="", status="ok", detail=""):
    try:
        CrawlLog.objects.create(
            user=user, task_id=task_id, platform=platform, keyword=keyword,
            status=status, detail=str(detail)[:500],
        )
    except Exception:
        logger.exception("log_crawl failed")


def cleanup_expired_data(days=None):
    """30 天数据自动清理"""
    days = days or settings.COMPLIANCE["data_retention_days"]
    cutoff = timezone.now() - timedelta(days=days)
    from apps.leads.models import Lead

    deleted, _ = Lead.objects.filter(created_at__lt=cutoff).delete()
    return deleted
