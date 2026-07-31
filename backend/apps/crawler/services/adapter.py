"""双模式适配：爬虫模式 / API 模式切换"""
from django.conf import settings


class AdapterService:
    """采集模式适配器：crawler（爬虫） / api（第三方 API）"""

    MODES = ("crawler", "api")

    def __init__(self):
        self.mode = "crawler"  # 默认爬虫模式
        self.api_providers = {}  # 预留：第三方数据 API 配置

    def set_mode(self, mode):
        if mode in self.MODES:
            self.mode = mode
            return True
        return False

    def get_mode(self):
        return self.mode

    def get_platform_status(self):
        """各平台采集可用状态"""
        from apps.crawler.services.crawler_service import CRAWLER_CLASSES

        return [
            {
                "platform": name,
                "name": {"douyin": "抖音", "xiaohongshu": "小红书", "kuaishou": "快手",
                         "weibo": "微博", "zhihu": "知乎", "tieba": "贴吧"}.get(name, name),
                "enabled": cls(settings.CRAWLER_SETTINGS).enabled if hasattr(cls(settings.CRAWLER_SETTINGS), "enabled") else True,
                "mode": self.mode,
            }
            for name, cls in CRAWLER_CLASSES.items()
        ]


adapter_service = AdapterService()
