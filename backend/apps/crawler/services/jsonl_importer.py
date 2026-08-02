# -*- coding: utf-8 -*-
"""MediaCrawler 真实数据导入服务
读取 MediaCrawler 采集的 jsonl 文件 → 映射为 Lead 线索入库（去重 + 意向评分 + 行业/地域/领域/场景标签）
支持多平台：weibo/dy(douyin)/xhs(xiaohongshu)/ks(kuaishou)/zhihu/tieba
"""
import json
from datetime import datetime
from pathlib import Path

from apps.crawler.services.intent_scoring import IntentScoring

MEDIACRAWLER_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "MediaCrawler"

# 平台映射: MediaCrawler 目录名 → 系统平台码
PLATFORM_MAP = {
    "weibo": "weibo",
    "dy": "douyin",
    "xhs": "xiaohongshu",
    "ks": "kuaishou",
    "zhihu": "zhihu",
    "tieba": "tieba",
    "bili": "bilibili",
}

PLATFORM_NAMES = {
    "weibo": "微博", "douyin": "抖音", "xiaohongshu": "小红书",
    "kuaishou": "快手", "zhihu": "知乎", "tieba": "贴吧", "bilibili": "哔哩哔哩",
}

# 地域识别词表（省市 + 常见城市，命中即填 region）
REGION_WORDS = [
    "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉", "西安", "南京",
    "苏州", "天津", "长沙", "郑州", "青岛", "宁波", "厦门", "合肥", "福州", "济南",
    "大连", "沈阳", "昆明", "南宁", "贵阳", "哈尔滨", "石家庄", "太原", "南昌", "长春",
    "广东", "江苏", "浙江", "山东", "四川", "湖北", "湖南", "河南", "河北", "福建",
    "安徽", "陕西", "辽宁", "云南", "贵州", "广西", "山西", "江西", "吉林", "黑龙江",
    "内蒙古", "新疆", "西藏", "甘肃", "青海", "宁夏", "海南",
]

# 场景/需求标签词表：命中关键词 → demand + tags
SCENE_WORDS = {
    "法律咨询": ["律师", "打官司", "起诉", "诉讼", "法律援助", "合同纠纷", "欠款", "赔偿", "劳动仲裁", "离婚", "继承", "刑事"],
    "装修家居": ["装修", "翻新", "防水", "全屋定制", "门窗", "瓷砖", "地板", "刷墙", "水电改造"],
    "家政服务": ["保洁", "家政", "月嫂", "保姆", "搬家", "除甲醛", "开荒", "家电清洗", "疏通"],
    "教育培训": ["培训", "报名", "课程", "考证", "学历", "升学", "辅导", "托管", "考公", "考研"],
    "医美健康": ["医美", "整形", "祛斑", "植发", "牙科", "体检", "健康", "减肥", "祛痘", "皮肤"],
    "汽车服务": ["二手车", "汽车", "车险", "保养", "维修", "贴膜", "租车", "验车", "过户"],
    "企业服务": ["注册公司", "代理记账", "商标", "资质", "财税", "记账", "工商"],
    "本地生活": ["美食", "探店", "团购", "景区", "门票", "酒店", "民宿", "餐厅"],
    "电商零售": ["淘宝", "拼多多", "抖音电商", "直播带货", "开店", "货源", "爆款", "选品"],
    "金融理财": ["贷款", "理财", "保险", "信用卡", "投资", "基金", "股票", "公积金"],
}

# 场景（领域）→ 行业映射（用于 tags 中的行业标签）
SCENE_INDUSTRY = {
    "法律咨询": "法律服务", "装修家居": "装修家居", "家政服务": "本地生活家政服务",
    "教育培训": "教育培训", "医美健康": "美业医美", "汽车服务": "汽车服务行业",
    "企业服务": "企业B端财税商务服务", "本地生活": "本地生活", "电商零售": "电商零售",
    "金融理财": "金融理财",
}


def _parse_time(value):
    """解析 MediaCrawler 时间字段 → datetime"""
    if not value:
        return None
    s = str(value).strip()
    try:
        if "+" in s or "-" in s and ":" in s and len(s) >= 19:
            s = s[:19]
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.fromtimestamp(float(value))
        except Exception:
            return None


def detect_region(text):
    """识别地域：命中省市词表 → 返回地域名"""
    if not text:
        return ""
    for r in REGION_WORDS:
        if r in text:
            return r
    return ""


def detect_scene(text):
    """识别场景/需求：命中场景词表 → 返回 (场景名, 行业名)"""
    if not text:
        return "", ""
    for scene, words in SCENE_WORDS.items():
        for w in words:
            if w in text:
                return scene, SCENE_INDUSTRY.get(scene, "")
    return "", ""


def _int_or_zero(v):
    try:
        return int(v)
    except Exception:
        return 0


def import_jsonl(user, platform="weibo", keyword="", task_id=""):
    """导入指定平台 jsonl → Lead 入库（带行业/地域/场景标签），返回统计。
    platform: 系统平台码（weibo/douyin/xiaohongshu/kuaishou/zhihu/tieba）或 MediaCrawler 目录名（wb/dy/xhs/ks/zhihu/tieba）
    """
    from apps.leads.models import Lead

    scoring = IntentScoring()

    # 目录名解析：系统码 → 目录名
    dir_map = {
        "weibo": "weibo", "douyin": "douyin", "xiaohongshu": "xhs",
        "kuaishou": "ks", "zhihu": "zhihu", "tieba": "tieba", "bilibili": "bili",
    }
    dir_name = dir_map.get(platform, platform)
    sys_platform = PLATFORM_MAP.get(dir_name, platform)
    platform_label = PLATFORM_NAMES.get(sys_platform, platform)

    base = MEDIACRAWLER_DIR / "data" / dir_name / "jsonl"
    # 兼容旧路径 data/jsonl/{dir}/jsonl（历史版本输出）
    legacy_base = MEDIACRAWLER_DIR / "data" / "jsonl" / dir_name / "jsonl"
    if not base.exists() and legacy_base.exists():
        base = legacy_base
    if not base.exists():
        return {"success": False, "error": f"jsonl dir not found: {base}"}

    files = sorted(base.glob("search_contents_*.jsonl"))
    if not files:
        return {"success": False, "error": f"no search jsonl found in {base}"}

    imported = 0
    skipped = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except Exception:
                    continue
                note_id = str(raw.get("note_id") or raw.get("id") or raw.get("aweme_id") or raw.get("video_id") or raw.get("item_id") or "")
                if not note_id:
                    continue
                # 去重：按 user + platform + item_id；已存在则补标签（upsert 更新 region/demand/tags）
                exist = Lead.objects.filter(user=user, platform=sys_platform, item_id=note_id).first()
                if exist:
                    # 已存在：只补行业/地域/场景标签（不覆盖原内容）
                    search_text = (exist.content or "")[:200] + (exist.title or "")
                    region = detect_region(search_text)
                    scene, industry = detect_scene(search_text)
                    tags = list(exist.tags or [])
                    changed = False
                    if industry and industry not in tags:
                        tags.append(industry)
                        changed = True
                    if scene and scene not in tags:
                        tags.append(scene)
                        changed = True
                    if region and region not in tags:
                        tags.append(region)
                        changed = True
                    if exist.region != region:
                        exist.region = region
                        changed = True
                    if exist.demand != scene:
                        exist.demand = scene
                        changed = True
                    if changed:
                        exist.tags = tags
                        exist.save()
                    skipped += 1
                    continue

                content = raw.get("content") or raw.get("desc") or raw.get("title") or ""
                title = content[:80] if content else (raw.get("title") or "")
                like_count = _int_or_zero(raw.get("liked_count") or raw.get("like_count"))
                comment_count = _int_or_zero(raw.get("comments_count") or raw.get("comment_count"))
                share_count = _int_or_zero(raw.get("shared_count") or raw.get("share_count"))
                author = raw.get("nickname") or raw.get("author") or raw.get("user_name") or ""
                author_id = raw.get("creator_hash") or raw.get("author_id") or ""
                note_url = raw.get("note_url") or raw.get("url") or ""

                item = {
                    "content": content,
                    "title": title,
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "share_count": share_count,
                }
                keywords = [keyword] if keyword else [raw.get("source_keyword") or ""]
                score, breakdown = scoring.score(item, keywords)
                if score >= 60:
                    intent_label = "high"
                elif score >= 40:
                    intent_label = "medium"
                elif score >= 20:
                    intent_label = "low"
                else:
                    intent_label = "none"

                # 行业/地域/场景识别
                search_text = content[:200] + title
                region = detect_region(search_text)
                scene, industry = detect_scene(search_text)
                tags = [platform_label, "真实数据"]
                if industry:
                    tags.append(industry)
                if scene:
                    tags.append(scene)
                if region:
                    tags.append(region)

                Lead.objects.create(
                    user=user,
                    task_id=task_id,
                    platform=sys_platform,
                    item_id=note_id,
                    title=title,
                    content=content,
                    author=author,
                    author_id=author_id,
                    url=note_url or raw.get("aweme_url") or raw.get("video_url") or f"https://m.weibo.cn/detail/{note_id}",
                    like_count=like_count,
                    comment_count=comment_count,
                    share_count=share_count,
                    publish_time=_parse_time(raw.get("create_date_time") or raw.get("create_time") or raw.get("publish_time")),
                    intent_score=score,
                    intent_label=intent_label,
                    score_breakdown=breakdown,
                    region=region,
                    demand=scene,
                    tags=tags,
                )
                imported += 1

    return {
        "success": True,
        "platform": sys_platform,
        "imported": imported,
        "skipped_dup": skipped,
        "files": [f.name for f in files],
    }


def import_weibo_jsonl(user, keyword="", task_id=""):
    """兼容旧函数名：导入微博 jsonl"""
    return import_jsonl(user, platform="weibo", keyword=keyword, task_id=task_id)
