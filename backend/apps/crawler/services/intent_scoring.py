"""意向打分：0-100 分加权算法
权重：内容长度 0.1 + 关键词匹配 0.4 + 情感 0.3 + 互动 0.2
"""
import re

POSITIVE_WORDS = [
    "想", "要", "求", "需要", "打算", "计划", "准备", "考虑", "咨询", "了解",
    "多少钱", "价格", "报价", "费用", "怎么收费", "划算", "求推荐", "推荐一下",
    "有没有", "哪里好", "怎么样", "靠谱", "求介绍", "联系", "电话", "上门",
    "急", "尽快", "马上", "预算", "方案", "装修中", "刚需", "在找", "寻找",
]
NEGATIVE_WORDS = [
    "不需要", "不用", "别", "勿", "拒绝", "讨厌", "坑", "骗", "垃圾", "差评",
    "后悔", "避雷", "踩坑", "千万别", "不建议", "投诉", "维权", "退款",
]
INTENT_KEYWORDS = ["买", "购", "选", "定", "约", "询", "问", "谈"]


class IntentScoring:
    """客户意向打分"""

    WEIGHTS = {"content_length": 0.1, "keyword_match": 0.4, "sentiment": 0.3, "interaction": 0.2}

    def __init__(self, weights=None):
        if weights:
            self.WEIGHTS.update(weights)

    @staticmethod
    def score_content_length(text):
        """内容长度得分 0-100"""
        length = len(text or "")
        if length >= 200:
            return 100
        if length >= 100:
            return 80
        if length >= 50:
            return 60
        if length >= 20:
            return 40
        return 20

    @staticmethod
    def score_keyword_match(text, keywords, negative_words=None):
        """关键词匹配得分 0-100：命中正词加 30/词，命中否定词减 40"""
        score = 0
        text = text or ""
        for kw in keywords or []:
            if kw and kw in text:
                score += 30
        for neg in negative_words or []:
            if neg and neg in text:
                score -= 40
        return max(0, min(100, score))

    @staticmethod
    def score_sentiment(text):
        """情感得分 0-100：正向词 +12/词，负向词 -15/词"""
        score = 50
        text = text or ""
        for w in POSITIVE_WORDS:
            if w in text:
                score += 12
        for w in NEGATIVE_WORDS:
            if w in text:
                score -= 15
        return max(0, min(100, score))

    @staticmethod
    def score_interaction(like_count, comment_count, share_count):
        """互动得分 0-100"""
        total = (like_count or 0) + (comment_count or 0) * 3 + (share_count or 0) * 5
        if total >= 1000:
            return 100
        if total >= 500:
            return 80
        if total >= 100:
            return 60
        if total >= 10:
            return 40
        return 20

    def score(self, item, keywords, negative_words=None):
        """综合打分，返回 (score, breakdown)"""
        text = item.get("content") or item.get("title") or ""
        s1 = self.score_content_length(text)
        s2 = self.score_keyword_match(text, keywords, negative_words)
        s3 = self.score_sentiment(text)
        s4 = self.score_interaction(
            item.get("like_count"), item.get("comment_count"), item.get("share_count")
        )
        total = (
            self.WEIGHTS["content_length"] * s1
            + self.WEIGHTS["keyword_match"] * s2
            + self.WEIGHTS["sentiment"] * s3
            + self.WEIGHTS["interaction"] * s4
        )
        return round(total), {"content_length": s1, "keyword_match": s2, "sentiment": s3, "interaction": s4}
