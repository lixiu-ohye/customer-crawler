"""内容解析：正文/评论/问答解析、时间筛选、地域提取"""
import re
from datetime import datetime, timedelta


class ContentParser:
    """解析与筛选工具"""

    @staticmethod
    def clean_text(text):
        """清洗文本：去 HTML、空白、表情符"""
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def extract_region(text):
        """从文本提取地域（省/市/区），返回 [province, city, district]"""
        if not text:
            return None
        provinces = [
            "北京", "上海", "天津", "重庆", "广东", "江苏", "浙江", "四川", "湖北",
            "湖南", "河南", "河北", "山东", "山西", "陕西", "福建", "安徽", "江西",
            "广西", "云南", "贵州", "辽宁", "吉林", "黑龙江", "甘肃", "青海", "宁夏",
            "新疆", "内蒙古", "西藏", "海南", "香港", "澳门", "台湾",
        ]
        city_hint = re.search(
            r"({})市|({})(?:市|区|县)|在({})".format("|".join(provinces), "|".join(provinces), "|".join(provinces)),
            text,
        )
        if city_hint:
            return [city_hint.group(0)[:2], city_hint.group(0), ""]
        # 直辖市直接命中
        for p in ("北京", "上海", "天津", "重庆"):
            if p in text:
                return [p, p, ""]
        return None

    @staticmethod
    def parse_time(raw, platform="weibo"):
        """解析各平台时间字符串 → datetime 或 None"""
        if not raw:
            return None
        try:
            if platform == "weibo":
                if isinstance(raw, str) and "分钟前" in raw:
                    minutes = int(re.search(r"\d+", raw).group())
                    return datetime.now() - timedelta(minutes=minutes)
                if isinstance(raw, str) and "小时前" in raw:
                    hours = int(re.search(r"\d+", raw).group())
                    return datetime.now() - timedelta(hours=hours)
                if isinstance(raw, str) and "昨天" in raw:
                    return datetime.now() - timedelta(days=1)
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone()
            if isinstance(raw, (int, float)):
                return datetime.fromtimestamp(raw)
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def within_days(raw, platform, days):
        """时间筛选：是否在 N 天内发布"""
        dt = ContentParser.parse_time(raw, platform)
        if dt is None:
            return True  # 无法判断时间默认放行
        return dt >= datetime.now() - timedelta(days=days)

    @staticmethod
    def extract_comments(text):
        """粗略提取评论/问答正文片段"""
        if not text:
            return []
        # 匹配引号包裹的短句，作为评论候选
        return re.findall(r"[“\"『「]([^”\"』」]{4,60})[”\"』」]", text)
