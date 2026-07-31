"""自动标签：地域 / 意向 / 平台 / 需求 四类标签"""
from apps.crawler.services.content_parser import ContentParser
from apps.crawler.services.intent_scoring import IntentScoring

TAG_RULES = {
    "装修": ["装修", "全屋定制", "整装", "家装", "旧房改造", "翻新", "泥瓦", "水电"],
    "教育": ["培训", "补习", "辅导", "早教", "编程", "留学", "考研", "网课"],
    "医疗": ["医美", "牙科", "口腔", "体检", "植发", "眼科", "中医", "祛痘"],
    "汽车": ["买车", "4S", "二手车", "洗车", "贴膜", "保养", "充电桩", "试驾"],
    "餐饮": ["加盟", "开店", "奶茶", "火锅", "烧烤", "小吃", "摆摊"],
    "家居": ["家具", "软装", "窗帘", "灯具", "床垫", "沙发", "定制家具"],
    "健身": ["健身房", "私教", "瑜伽", "普拉提", "减脂", "增肌"],
    "母婴": ["月子中心", "月嫂", "育儿", "奶粉", "待产", "产后"],
    "金融": ["贷款", "信用卡", "理财", "保险", "pos机", "借款"],
    "企服": ["公司注册", "代理记账", "商标", "小程序", "网站建设", "营业执照"],
}


class AutoTagging:
    """自动标签生成"""

    @staticmethod
    def region_tag(text):
        """地域标签"""
        region = ContentParser.extract_region(text)
        if region:
            return region[0] + ("市" if len(region[0]) == 2 and region[0] not in ("北京", "上海", "天津", "重庆") else "")
        return "未知地域"

    @staticmethod
    def intent_tag(score):
        """意向标签"""
        if score >= 80:
            return "高意向"
        if score >= 60:
            return "中意向"
        if score >= 40:
            return "低意向"
        return "无意向"

    @staticmethod
    def platform_tag(platform):
        return {"douyin": "抖音", "xiaohongshu": "小红书", "kuaishou": "快手",
                "weibo": "微博", "zhihu": "知乎", "tieba": "贴吧"}.get(platform, platform)

    @staticmethod
    def demand_tag(text):
        """需求标签：命中规则返回行业需求"""
        for tag, words in TAG_RULES.items():
            for w in words:
                if w in (text or ""):
                    return tag
        return "其他"

    @staticmethod
    def generate(item, score=None):
        """生成四类标签"""
        text = item.get("content") or item.get("title") or ""
        if score is None:
            score, _ = IntentScoring().score(item, [])
        return {
            "region": AutoTagging.region_tag(text),
            "intent": AutoTagging.intent_tag(score),
            "platform": AutoTagging.platform_tag(item.get("platform", "")),
            "demand": AutoTagging.demand_tag(text),
        }
