"""关键词服务：增删改查、批量导入、jieba 联想、AI 拓词、否定词过滤"""
import re

from django.db.models import Q

from apps.keywords.models import Keyword, KeywordGroup

try:
    import jieba
    import jieba.analyse

    _JIEBA_OK = True
except ImportError:
    _JIEBA_OK = False


class KeywordService:
    """关键词业务逻辑"""

    # 行业地点联想词典：行业 + 城市/区域 → 组合词
    INDUSTRY_DICT = {
        "装修": ["装修", "全屋定制", "整装", "家装", "旧房改造", "翻新"],
        "教育": ["培训", "补习", "辅导班", "早教", "少儿编程", "留学", "考研"],
        "医疗": ["医美", "牙科", "口腔", "体检", "植发", "眼科", "中医"],
        "汽车": ["买车", "4S店", "二手车", "洗车", "贴膜", "保养", "充电桩"],
        "餐饮": ["加盟", "开店", "奶茶", "火锅", "烧烤", "小吃培训"],
        "家居": ["家具", "定制家具", "软装", "窗帘", "灯具", "床垫"],
        "健身": ["健身房", "私教", "瑜伽", "普拉提", "减脂"],
        "母婴": ["月子中心", "月嫂", "育儿", "奶粉", "早教"],
        "金融": ["贷款", "信用卡", "理财", "保险", "pos机"],
        "企服": ["公司注册", "代理记账", "商标注册", "小程序开发", "网站建设"],
    }
    CITY_DICT = [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都", "重庆", "武汉",
        "西安", "长沙", "郑州", "青岛", "大连", "厦门", "福州", "合肥", "宁波", "无锡",
        "佛山", "东莞", "天津", "济南", "沈阳", "昆明", "贵阳", "南宁", "石家庄", "哈尔滨",
    ]

    @staticmethod
    def create(user, word, group_id=None, negative_words=""):
        group = None
        if group_id:
            group = KeywordGroup.objects.filter(id=group_id, user=user).first()
        return Keyword.objects.create(
            user=user, word=word.strip(), group=group, negative_words=negative_words
        )

    @staticmethod
    def bulk_import(user, words):
        """批量导入，自动去重"""
        created, skipped = 0, 0
        for raw in words:
            word = raw.strip()
            if not word:
                continue
            if Keyword.objects.filter(user=user, word=word).exists():
                skipped += 1
                continue
            KeywordService.create(user, word)
            created += 1
        return {"created": created, "skipped": skipped}

    @staticmethod
    def suggest(user, prefix, limit=10):
        """自动联想：jieba 分词 + 前缀模糊匹配 + 热度排序"""
        prefix = prefix.strip()
        if not prefix:
            return []
        qs = Keyword.objects.filter(user=user).filter(Q(word__icontains=prefix))
        results = list(qs.values_list("word", flat=True)[:limit])
        if _JIEBA_OK and len(results) < limit:
            # 对前缀做 jieba 切词，扩展联想
            for token in jieba.cut_for_search(prefix):
                if len(token) >= 2 and len(results) < limit:
                    extra = list(
                        Keyword.objects.filter(user=user, word__icontains=token)
                        .exclude(word__in=results)
                        .values_list("word", flat=True)[: limit - len(results)]
                    )
                    results.extend(extra)
        return results

    @staticmethod
    def ai_expand(user, seed, industry=None, city=None):
        """AI 拓词（规则引擎模拟；可对接大模型 API）：
        行业词 × 城市词 组合 + 同义词扩展
        """
        base = [seed]
        if industry and industry in KeywordService.INDUSTRY_DICT:
            base.extend(KeywordService.INDUSTRY_DICT[industry])
        city = city or "全国"
        expanded = set(base)
        if city != "全国":
            expanded.update([f"{city}{w}" for w in base])
        # 同义词/近义扩展
        synonym_map = {
            "装修": ["装饰", "翻新", "改造"],
            "贷款": ["借款", "信贷", "融资"],
            "加盟": ["加盟合作", "开店", "招商"],
            "培训": ["课程", "学习班", "集训"],
        }
        for w in base:
            for syn in synonym_map.get(w, []):
                expanded.add(syn)
                if city != "全国":
                    expanded.add(f"{city}{syn}")
        expanded.discard(seed)
        created, skipped = 0, 0
        for w in expanded:
            if Keyword.objects.filter(user=user, word=w).exists():
                skipped += 1
                continue
            KeywordService.create(user, w)
            created += 1
        return {"expanded": sorted(expanded), "created": created, "skipped": skipped}

    @staticmethod
    def filter_negative(text, negative_words):
        """否定词过滤：命中任一否定词返回 True"""
        if not negative_words:
            return False
        for neg in negative_words.replace("，", ",").split(","):
            neg = neg.strip()
            if neg and neg in text:
                return True
        return False

    @staticmethod
    def extract_negative_keywords(keywords):
        """从关键词列表中提取否定词集合"""
        neg_set = set()
        for kw in keywords:
            if kw.negative_words:
                for neg in kw.negative_words.replace("，", ",").split(","):
                    neg = neg.strip()
                    if neg:
                        neg_set.add(neg)
        return neg_set
