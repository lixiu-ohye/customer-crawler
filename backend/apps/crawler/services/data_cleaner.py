"""数据清洗：去重、过滤空数据/广告/营销号、清洗文本"""
import re

from apps.crawler.services.content_parser import ContentParser

AD_PATTERNS = [
    r"加微信[^ ]{0,20}",
    r"VX[:：]?\s?\w+",
    r"薇信[:：]?\s?\w+",
    r"q{1,3}[:：]?\s?\d{5,12}",
    r"QQ[:：]?\s?\d{5,12}",
    r"点击(链接|下方|蓝字)",
    r"私信我[^。]{0,20}(领取|获取|报名)",
    r"关注[^。]{0,15}(领取|抽奖|福利)",
    r"https?://\S+",
    r"淘宝|京东|拼多多|下单链接",
]

MARKETING_AUTHOR_HINTS = ["营销", "推广", "广告", "代运营", "刷单", "客服", "种草君", "好物推荐"]


class DataCleaner:
    """线索数据清洗"""

    @staticmethod
    def is_ad_content(text):
        """广告内容识别"""
        if not text:
            return False
        hits = sum(1 for p in AD_PATTERNS if re.search(p, text))
        return hits >= 1

    @staticmethod
    def is_marketing_author(author):
        """营销号识别"""
        if not author:
            return False
        return any(h in author for h in MARKETING_AUTHOR_HINTS)

    @staticmethod
    def clean_content(text):
        """清洗正文：去广告痕迹、压缩空白"""
        text = ContentParser.clean_text(text)
        for p in AD_PATTERNS:
            text = re.sub(p, "", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def dedupe(items, key_fn=None):
        """按 key 去重，保留第一条"""
        key_fn = key_fn or (lambda it: it.get("item_id") or it.get("content", "")[:50])
        seen = set()
        result = []
        for item in items:
            key = key_fn(item)
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            result.append(item)
        return result

    @staticmethod
    def process_batch(items):
        """批量清洗管线：去空 → 去广告 → 去营销号 → 去重 → 清洗文本"""
        cleaned = []
        for item in items:
            if not item.get("content"):
                continue
            if DataCleaner.is_ad_content(item["content"]):
                continue
            if DataCleaner.is_marketing_author(item.get("author", "")):
                continue
            item["content"] = DataCleaner.clean_content(item["content"])
            item["title"] = DataCleaner.clean_content(item.get("title", ""))[:100]
            if not item["content"]:
                continue
            cleaned.append(item)
        return DataCleaner.dedupe(cleaned)
