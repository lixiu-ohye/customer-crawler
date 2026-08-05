# -*- coding: utf-8 -*-
"""
宠物行业专项评论扫描器 v2

从 MediaCrawler 评论 jsonl 中提取宠物相关评论 → 轻量需求识别 →
GLM 深度筛选 → 有需求的评论用户入库成线索（is_customer=True 才算客户）

用法：
  python pet_scan_comments.py              # 扫描所有平台最近评论
  python pet_scan_comments.py --platform douyin,xiaohongshu
  python pet_scan_comments.py --glm-only   # 只跑 GLM 深度筛选（对已有候选）
"""
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

import django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.leads.models import Lead
from apps.monitor.models import RawComment, IntentComment
from apps.crawler.services.customer_ai_filter import CustomerAIFilter

# 平台目录映射
PLATFORM_DIR = {
    "douyin": "douyin", "xiaohongshu": "xhs", "weibo": "weibo",
    "tieba": "tieba", "kuaishou": "kuaishou", "zhihu": "zhihu", "bilibili": "bili",
}
PLATFORM_NAMES = {
    "douyin": "抖音", "xiaohongshu": "小红书", "weibo": "微博", "tieba": "贴吧",
    "kuaishou": "快手", "zhihu": "知乎", "bilibili": "哔哩哔哩",
}

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"

# ============ 宠物实体词（评论必须提到宠物） ============
PET_ENTITY_WORDS = [
    "宠物", "猫", "狗", "猫咪", "狗狗", "主子", "毛孩子", "铲屎",
    "猫粮", "狗粮", "猫砂", "罐头", "喵", "汪", "小奶猫", "小奶狗",
    "寄养", "绝育", "疫苗", "驱虫", "宠物医院", "宠物店", "宠物美容",
    "宠物洗澡", "宠物用品", "遛狗", "撸猫", "逗猫", "牵引", "狗窝", "猫窝",
    "兔子", "仓鼠", "乌龟", "金鱼", "猫砂盆", "猫爬架", "化毛膏", "益生菌",
    "vet", "兽医", "犬", "猫舍", "狗舍", "宠物托运", "宠物粮", "宠物零食",
]

# ============ 宠物需求词 ============
PET_NEED_KEYWORDS = [
    "多少钱", "价格", "怎么", "哪里", "哪家", "求推荐", "求", "求助", "问问",
    "问一下", "请问", "寄养", "绝育", "驱虫", "疫苗", "洗澡", "美容", "看病", "治疗",
    "宠物医院", "宠物店", "宠物美容", "多少钱合适", "贵不贵", "便宜点",
    "有推荐的吗", "推荐哪家", "哪个好", "哪个靠谱", "第一次养", "新手养", "要注意什么",
    "猫咪老是", "狗狗老是", "猫猫老是", "猫吐", "狗拉", "猫拉稀", "狗拉稀",
]

# 否定词：纯情感/分享/广告
PET_NEGATIVE_KEYWORDS = [
    "好可爱", "太可爱", "可爱死了", "萌翻了", "哈哈", "哈哈哈", "笑死",
    "教程", "分享", "攻略", "干货", "博主", "自媒体", "推广", "加盟",
    "批发", "代理", "招聘", "培训", "不推荐", "避雷", "别去", "骗人", "垃圾",
]

# 子领域
PET_SUB_INDUSTRIES = {
    "宠物医疗": ["医院", "看病", "治疗", "绝育", "疫苗", "驱虫", "手术", "体检", "生病", "呕吐", "拉稀", "皮肤病"],
    "宠物美容": ["洗澡", "美容", "剪毛", "spa", "造型"],
    "宠物食品": ["猫粮", "狗粮", "罐头", "零食", "营养", "益生菌", "化毛膏"],
    "宠物寄养": ["寄养", "托管", "托运", "代养"],
    "宠物用品": ["笼子", "牵引", "窝", "玩具", "猫砂", "猫爬架", "自动"],
    "宠物零售": ["买猫", "买狗", "卖猫", "卖狗", "猫舍", "狗舍", "领养", "价格"],
}


def is_pet_related(content: str) -> bool:
    if not content:
        return False
    return any(w in content for w in PET_ENTITY_WORDS)


def is_pet_need(content: str):
    """返回 (is_need, confidence, hit_industries)"""
    if not content:
        return False, "empty", []
    if not is_pet_related(content):
        return False, "not_pet_related", []
    neg_hit = any(w in content for w in PET_NEGATIVE_KEYWORDS)
    need_hit = [w for w in PET_NEED_KEYWORDS if w in content]
    if neg_hit and not need_hit:
        return False, "negative", []
    if not need_hit:
        return False, "no_need", []
    hit_inds = [ind for ind, words in PET_SUB_INDUSTRIES.items() if any(w in content for w in words)]
    score = len(need_hit)
    if any(w in content for w in ["多少钱", "价格", "怎么", "哪里", "哪家", "求推荐", "求助"]):
        score += 2
    if any(c in content for c in ["？", "?", "怎么", "能不能"]):
        score += 1
    confidence = "high" if score >= 3 else "medium" if score >= 1 else "low"
    return score >= 1, confidence, hit_inds


def need_score(content: str) -> int:
    if not content:
        return 0
    base = 25
    for w in PET_NEED_KEYWORDS:
        if w in content:
            base += 8
    if any(w in content for w in ["多少钱", "价格", "贵不贵"]):
        base += 15
    if any(c in content for c in ["？", "?", "怎么"]):
        base += 10
    if any(w in content for w in ["求推荐", "求助", "请问", "问一下"]):
        base += 12
    return min(100, base)


# 城市列表
CITIES = ["北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "南京", "西安",
          "重庆", "天津", "苏州", "长沙", "郑州", "东莞", "青岛", "沈阳",
          "宁波", "昆明", "大连", "哈尔滨", "长春", "福州", "厦门", "合肥",
          "济南", "温州", "南宁", "贵阳", "石家庄", "泉州", "烟台", "太原",
          "南昌", "中山", "扬州", "兰州", "呼和浩特", "乌鲁木齐", "珠海",
          "唐山", "保定", "廊坊", "衡水", "沧州", "邯郸", "秦皇岛", "邢台",
          "张家口", "承德", "衡阳", "株洲", "湘潭", "莆田", "漳州",
          "龙岩", "三明", "南平", "宁德", "九江", "赣州", "吉安", "宜春", "抚州",
          "上饶", "景德镇", "萍乡", "新余", "鹰潭", "开封", "洛阳", "平顶山"]


def extract_city(content: str) -> str:
    if not content:
        return ""
    for city in CITIES:
        if city in content:
            return city
    return ""


def collect_comment_files(days=3):
    """收集各平台评论文件"""
    result = {}
    cutoff = datetime.now() - timedelta(days=days)
    for plat, dirname in PLATFORM_DIR.items():
        out_dir = MEDIACRAWLER_DIR / "data" / dirname / "jsonl"
        if not out_dir.exists():
            continue
        files = []
        for f in sorted(out_dir.glob("search_comments_*.jsonl")):
            try:
                if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff:
                    files.append(f)
            except Exception:
                continue
        if files:
            result[plat] = files
    return result


def scan_files(days=3, max_per_platform=800):
    """扫描评论文件，提取宠物需求评论并入库"""
    plat_files = collect_comment_files(days)
    print(f"[宠物扫描] 平台文件: { {k: [f.name for f in v] for k, v in plat_files.items()} }")

    total_scanned = 0
    pet_hits = 0
    new_leads = 0
    for plat, files in plat_files.items():
        plat_count = 0
        for f in files:
            print(f"[宠物扫描] 读 {f.name} ...")
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    total_scanned += 1
                    try:
                        raw = json.loads(line)
                    except Exception:
                        continue
                    # 提取评论
                    content = str(raw.get("content") or raw.get("text") or raw.get("comment_text") or "").strip()
                    if not content:
                        continue
                    is_need, conf, hit_inds = is_pet_need(content)
                    if not is_need:
                        continue
                    pet_hits += 1
                    plat_count += 1
                    if plat_count > max_per_platform:
                        break

                    # 提取用户/ID
                    comment_id = str(raw.get("comment_id") or raw.get("cid") or "")
                    user = raw.get("user") or {}
                    uid = str(user.get("id") or user.get("uid") or user.get("user_id") or raw.get("creator_hash") or raw.get("user_id") or "")
                    nickname = str(user.get("nickname") or user.get("name") or raw.get("user_nickname") or raw.get("nickname") or "")
                    url = str(raw.get("note_url") or raw.get("aweme_url") or raw.get("url") or raw.get("link") or "")
                    like_count = int(raw.get("like_count") or raw.get("comment_like_count") or 0)
                    reply_count = int(raw.get("reply_count") or raw.get("sub_comment_count") or 0)

                    # 幂等：按 platform+comment_id 查
                    if comment_id and Lead.objects.filter(platform=plat, item_id=comment_id).exists():
                        continue
                    if not comment_id and not uid:
                        continue

                    score = need_score(content)
                    tags = list(set(["宠物行业", "真实数据"] + hit_inds))
                    region = extract_city(content)
                    item_id = comment_id or (uid + "_" + str(hash(content) % 100000))

                    # 获取默认用户（admin）
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    owner = User.objects.filter(username="admin").first()
                    if not owner:
                        continue

                    Lead.objects.create(
                        user=owner,
                        platform=plat,
                        item_id=item_id,
                        title="",
                        content=content[:300],
                        author=nickname,
                        author_id=uid,
                        url=url,
                        like_count=like_count,
                        comment_count=reply_count,
                        share_count=0,
                        region=region,
                        demand="宠物行业需求",
                        intent_score=score,
                        intent_label="high" if score >= 60 else "medium" if score >= 40 else "low",
                        tags=tags,
                        is_customer=None,  # 待 GLM 确认
                        contact_hint="platform_id",
                    )
                    new_leads += 1
            if plat_count > max_per_platform:
                break
        print(f"[宠物扫描] {plat}: 宠物需求评论 {plat_count}")

    print(f"\n[宠物扫描] 完成: 扫描 {total_scanned} 条评论, 宠物需求 {pet_hits}, 新增线索 {new_leads}")
    return new_leads


def glm_deep_filter(limit=None):
    """对 is_customer=None 的宠物线索做 GLM 深度筛选"""
    qs = Lead.objects.filter(is_customer__isnull=True)
    # 用 tags 判断宠物相关（内存过滤）
    all_pending = [l for l in qs if l.tags and any("宠物" in str(t) for t in l.tags)]
    if limit:
        all_pending = all_pending[:limit]
    if not all_pending:
        print("[宠物GLM] 无待筛选宠物线索")
        return 0

    print(f"[宠物GLM] 待筛选 {len(all_pending)} 条宠物线索...")
    ai = CustomerAIFilter()
    done = 0
    batch_size = 12
    for i in range(0, len(all_pending), batch_size):
        batch = all_pending[i:i + batch_size]
        texts = [{"title": "", "content": l.content or ""} for l in batch]
        try:
            results = ai.classify_batch(texts)
        except Exception as e:
            print(f"  GLM batch {i} failed: {e}")
            results = [None] * len(texts)
        for lead, result in zip(batch, results):
            if result is None:
                continue
            is_cust = bool(result.get("is_customer", False))
            lead.is_customer = is_cust
            lead.customer_type = result.get("customer_type")
            lead.customer_reason = (result.get("reason") or "")[:200]
            lead.needs = result.get("needs") or ""
            if is_cust:
                lead.contact_hint = result.get("contact_hint") or "platform_id"
            lead.save(update_fields=["is_customer", "customer_type", "customer_reason", "needs", "contact_hint"])
            done += 1
        time.sleep(0.3)
    print(f"[宠物GLM] 完成 {done} 条")
    return done


def main():
    import argparse
    parser = argparse.ArgumentParser(description="宠物行业评论区获客")
    parser.add_argument("--platform", default="", help="平台过滤（逗号分隔）")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--glm-only", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    t0 = datetime.now()
    if args.glm_only:
        glm_deep_filter(args.limit)
    else:
        scan_files(days=args.days)
        glm_deep_filter(args.limit)

    # 统计
    all_leads = list(Lead.objects.all())
    pet_leads = [l for l in all_leads if l.tags and any("宠物" in str(t) for t in l.tags)]
    cust = sum(1 for l in pet_leads if l.is_customer is True)
    non = sum(1 for l in pet_leads if l.is_customer is False)
    pend = sum(1 for l in pet_leads if l.is_customer is None)
    print(f"\n=== 宠物线索统计 === 总计 {len(pet_leads)} | 客户 {cust} | 非客户 {non} | 待确认 {pend}")
    print(f"耗时 {(datetime.now() - t0).total_seconds():.1f}s")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

