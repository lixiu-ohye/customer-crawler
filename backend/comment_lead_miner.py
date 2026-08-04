# -*- coding: utf-8 -*-
"""评论区获客矿工：从搜索结果的评论区挖掘潜在客户
流程：扫描 MediaCrawler 各平台 search_comments_*.jsonl（搜索时顺带抓取的评论）
→ 去重入库 RawComment → 意向评分 IntentComment → 转线索 Lead（is_customer 走 GLM 筛选）
支持平台：douyin/xiaohongshu/weibo/tieba/kuaishou/zhihu/bilibili
用法：python comment_lead_miner.py [--platform douyin,xiaohongshu] [--days 2] [--convert]
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.monitor.models import RawComment, IntentComment
from apps.crawler.services.intent_scoring import IntentScoring
from apps.crawler.services.customer_ai_filter import CustomerAIFilter

logger = logging.getLogger("comment_lead_miner")

# MediaCrawler 目录（workspace/MediaCrawler）
WORKSPACE_DIR = BACKEND_DIR.parent.parent
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"

# 平台码 → 输出目录名
PLATFORM_DIR = {
    "douyin": "douyin", "xiaohongshu": "xhs", "weibo": "weibo",
    "tieba": "tieba", "kuaishou": "kuaishou", "zhihu": "zhihu", "bilibili": "bili",
}
PLATFORM_NAMES = {
    "douyin": "抖音", "xiaohongshu": "小红书", "weibo": "微博", "tieba": "贴吧",
    "kuaishou": "快手", "zhihu": "知乎", "bilibili": "哔哩哔哩",
}

# 每平台每次最多导入评论数
MAX_PER_PLATFORM = 500


def collect_comment_files(platform, days):
    """收集指定平台最近 N 天的 search_comments jsonl"""
    out_dir = MEDIACRAWLER_DIR / "data" / PLATFORM_DIR.get(platform, platform) / "jsonl"
    if not out_dir.exists():
        return []
    cutoff = datetime.now() - timedelta(days=days)
    files = []
    for f in sorted(out_dir.glob("search_comments_*.jsonl")):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime >= cutoff:
                files.append(f)
        except Exception:
            continue
    return files


def extract_comment(raw, platform):
    """从 jsonl 行提取评论字段（兼容多平台格式）"""
    if not isinstance(raw, dict):
        return None
    # 通用字段
    comment_id = str(raw.get("comment_id") or raw.get("cid") or "")
    content = str(raw.get("content") or raw.get("text") or raw.get("comment_text") or "").strip()
    if not content or not comment_id:
        return None

    user = raw.get("user") or {}
    if not isinstance(user, dict):
        user = {}
    # 贴吧格式：creator_hash/user_nickname；通用：user.id/nickname
    uid = str(user.get("id") or user.get("uid") or user.get("user_id") or raw.get("creator_hash") or raw.get("user_id") or "")
    nickname = str(user.get("nickname") or user.get("name") or raw.get("user_nickname") or "")
    avatar = str(user.get("avatar_url") or user.get("avatar") or "")
    fan_cnt = 0
    try:
        fan_cnt = int(user.get("follower_count") or user.get("fans_count") or raw.get("fan_count") or 0)
    except Exception:
        pass
    region = str(user.get("region") or raw.get("region") or "")

    like_count = 0
    reply_count = 0
    try:
        like_count = int(raw.get("like_count") or raw.get("digg_count") or 0)
        reply_count = int(raw.get("reply_count") or raw.get("sub_comment_count") or 0)
    except Exception:
        pass

    parent_comment_id = str(raw.get("parent_comment_id") or "")

    # 时间解析
    comment_time = None
    ts = raw.get("create_time") or raw.get("publish_time") or raw.get("timestamp") or raw.get("last_modify_ts")
    if ts:
        s = str(ts)
        try:
            if s.isdigit() and len(s) > 10:
                comment_time = datetime.fromtimestamp(int(s) / 1000)
            elif s.isdigit():
                comment_time = datetime.fromtimestamp(int(s))
            else:
                comment_time = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            comment_time = None

    # 内容 URL（note_url / url）
    url = str(raw.get("note_url") or raw.get("url") or raw.get("share_url") or "")

    return {
        "comment_id": comment_id,
        "content": content[:500],
        "uid": uid,
        "nickname": nickname,
        "avatar_url": avatar,
        "fan_cnt": fan_cnt,
        "region": region,
        "like_count": like_count,
        "reply_count": reply_count,
        "parent_comment_id": parent_comment_id,
        "comment_time": comment_time,
        "url": url,
        "item_id": str(raw.get("note_id") or raw.get("aweme_id") or raw.get("item_id") or raw.get("video_id") or ""),
    }


def get_or_create_aggregate_target(platform, user):
    """为搜索评论创建/获取聚合目标（满足 RawComment.target 外键非空）"""
    from apps.monitor.models import MonitorTarget
    target, _ = MonitorTarget.objects.get_or_create(
        platform=platform,
        target_type="competitor_account",
        target_id="__search_comments__",
        defaults={
            "title": f"{PLATFORM_NAMES.get(platform, platform)} 搜索评论区获客",
            "created_by": user,
        },
    )
    return target


def import_platform(platform, days, ai_filter):
    """导入一个平台的评论，返回统计"""
    files = collect_comment_files(platform, days)
    if not files:
        logger.info("[%s] 无评论文件", platform)
        return {"platform": platform, "files": 0, "comments": 0, "leads": 0, "customers": 0}

    sys_platform = platform
    intent_scoring = IntentScoring()
    imported = 0
    skipped = 0
    leads_created = 0
    customers = 0
    pending_glm = []  # [(lead, content)]

    # 找出系统用户（admin）
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.filter(username="admin").first()
    # 聚合目标
    aggregate_target = get_or_create_aggregate_target(platform, user) if user else None

    for cf in files:
        logger.info("[%s] 处理评论文件: %s", platform, cf.name)
        try:
            with open(cf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except Exception:
                        continue
                    data = extract_comment(raw, platform)
                    if not data:
                        continue

                    # 幂等去重
                    if RawComment.objects.filter(platform=sys_platform, comment_id=data["comment_id"]).exists():
                        skipped += 1
                        continue

                    # 创建 RawComment（挂聚合目标）
                    comment = RawComment.objects.create(
                        target=aggregate_target,
                        platform=sys_platform,
                        comment_id=data["comment_id"],
                        uid=data["uid"],
                        nickname=data["nickname"],
                        avatar_url=data["avatar_url"],
                        fan_cnt=data["fan_cnt"],
                        region=data["region"],
                        content=data["content"],
                        like_count=data["like_count"],
                        reply_count=data["reply_count"],
                        parent_comment_id=data["parent_comment_id"],
                        comment_time=data["comment_time"],
                    )

                    # 意向评分
                    try:
                        score, breakdown = intent_scoring.score({"content": data["content"]}, [])
                        level = "llm_pass" if score >= 70 else ("nlp_pass" if score >= 50 else "kw_only")
                        IntentComment.objects.create(
                            raw_comment=comment, intent_score=score, hit_keyword="",
                            level=level, is_ad=False, is_converted=False, llm_raw=breakdown,
                        )
                    except Exception as e:
                        logger.warning("[%s] 意向评分失败: %s", platform, e)

                    imported += 1

                    # 转线索（评论用户 → Lead）
                    if not user:
                        continue
                    from apps.leads.models import Lead
                    if Lead.objects.filter(platform=sys_platform, author_id=data["uid"]).exists():
                        continue
                    lead = Lead.objects.create(
                        user=user,
                        platform=sys_platform,
                        item_id=data["item_id"],
                        title=f"{data['nickname']}的评论",
                        content=data["content"],
                        author=data["nickname"],
                        author_id=data["uid"],
                        url=data["url"],
                        like_count=data["like_count"],
                        comment_count=data["reply_count"],
                        publish_time=data["comment_time"],
                        region=data["region"],
                        demand="",
                        intent_label="",
                        intent_score=0,
                        score_breakdown={},
                        is_customer=None,
                        customer_type="",
                        customer_reason="",
                        contact_hint="",
                        needs="",
                        tags=[PLATFORM_NAMES.get(platform, platform), "评论线索"],
                        status="new",
                        note=f"来源：{platform} 评论区获客",
                    )
                    leads_created += 1
                    # GLM 分批筛选（攒 12 条一批）
                    pending_glm.append((lead, data["content"]))
                    if len(pending_glm) >= 12:
                        customers += run_glm_batch(pending_glm, ai_filter)
                        pending_glm = []

        except Exception as e:
            logger.error("[%s] 文件处理失败 %s: %s", platform, cf.name, e)

    # 处理剩余批次
    if pending_glm:
        customers += run_glm_batch(pending_glm, ai_filter)

    logger.info("[%s] 完成: 评论 %d (skip %d), 线索 %d, 客户 %d",
                platform, imported, skipped, leads_created, customers)
    return {"platform": platform, "files": len(files), "comments": imported,
            "leads": leads_created, "customers": customers}


def run_glm_batch(batch, ai_filter):
    """对一批 (lead, content) 做 GLM 客户筛选"""
    if not ai_filter or not ai_filter.enabled:
        return 0
    customers = 0
    try:
        items = [{"title": "", "content": c[:300], "author": "", "platform": ""} for _, c in batch]
        results = ai_filter.classify_batch(items)
        for (lead, _), res in zip(batch, results or []):
            if not res:
                continue
            is_cust = res.get("is_customer")
            if is_cust is True:
                lead.is_customer = True
                lead.customer_type = str(res.get("customer_type") or "medium")
                lead.needs = str(res.get("needs") or "")[:100]
                lead.tags = list(lead.tags or []) + ["客户"]
                customers += 1
            elif is_cust is False:
                lead.is_customer = False
            lead.save()
        return customers
    except Exception as e:
        logger.warning("GLM 批次筛选失败: %s", e)
        return 0


def backfill_glm(ai_filter):
    """补跑：对 is_customer=None 的评论线索执行 GLM 筛选"""
    from apps.leads.models import Lead
    qs = Lead.objects.filter(note__startswith="来源：", is_customer__isnull=True)
    total = qs.count()
    logger.info("补跑 GLM 筛选: 待分类评论线索 %d 条", total)
    if not total:
        return 0
    customers = 0
    batch = []
    for lead in qs.iterator():
        batch.append((lead, lead.content or ""))
        if len(batch) >= 12:
            customers += run_glm_batch(batch, ai_filter)
            batch = []
    if batch:
        customers += run_glm_batch(batch, ai_filter)
    logger.info("补跑完成: 新增客户 %d", customers)
    return customers


def main():
    import argparse
    parser = argparse.ArgumentParser(description="评论区获客矿工")
    parser.add_argument("--platform", default="", help="平台逗号分隔，默认全部")
    parser.add_argument("--days", type=int, default=2, help="扫描最近 N 天文件")
    parser.add_argument("--convert", action="store_true", help="仅转换不重新导入（预留）")
    parser.add_argument("--backfill", action="store_true", help="只补跑 GLM 筛选（不导入新评论）")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BACKEND_DIR / "comment_lead_miner.log", encoding="utf-8"),
        ],
    )

    ai_filter = CustomerAIFilter()
    logger.info("GLM 筛选: %s (fallback g2claw: %s)",
                "启用" if ai_filter.enabled else "未启用（API key 缺失）",
                "启用" if ai_filter.fallback_enabled else "未启用")

    if args.backfill:
        backfill_glm(ai_filter)
        return

    platforms = [p.strip() for p in args.platform.split(",") if p.strip()] if args.platform else list(PLATFORM_DIR.keys())
    logger.info("=== 评论区获客矿工启动: platforms=%s days=%d ===", platforms, args.days)

    ai_filter = CustomerAIFilter()
    logger.info("GLM 筛选: %s (fallback g2claw: %s)",
                "启用" if ai_filter.enabled else "未启用（API key 缺失）",
                "启用" if ai_filter.fallback_enabled else "未启用")

    total = {"comments": 0, "leads": 0, "customers": 0}
    for p in platforms:
        r = import_platform(p, args.days, ai_filter)
        total["comments"] += r["comments"]
        total["leads"] += r["leads"]
        total["customers"] += r["customers"]

    logger.info("=== 汇总: 评论 %d, 线索 %d, 客户 %d ===", total["comments"], total["leads"], total["customers"])


if __name__ == "__main__":
    main()
