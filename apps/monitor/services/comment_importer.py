# -*- coding: utf-8 -*-
"""评论采集数据导入服务
读取 MediaCrawler 评论输出（jsonl 目录）→ 写入 RawComment（comment_id 幂等 upsert）→ 提取评论用户信息
支持多平台：douyin/kuaishou/shipinhao/weibo/xhs/zhihu/tieba/bili
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from apps.monitor.models import MonitorTarget, RawComment, IntentComment
from apps.crawler.services.intent_scoring import IntentScoring

logger = logging.getLogger("comment_importer")

# MediaCrawler 目录路径
MEDIACRAWLER_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "MediaCrawler"

# 平台映射：MediaCrawler 平台码 → 系统平台码
PLATFORM_MAP = {
    "dy": "douyin",
    "ks": "kuaishou", 
    "wb": "weibo",
    "xhs": "xiaohongshu",
    "zhihu": "zhihu",
    "tieba": "tieba",
    "bili": "bilibili",
}

# 平台名称
PLATFORM_NAMES = {
    "douyin": "抖音", "kuaishou": "快手", "xiaohongshu": "小红书",
    "weibo": "微博", "zhihu": "知乎", "tieba": "贴吧", "bilibili": "哔哩哔哩",
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


def _int_or_zero(v):
    try:
        return int(v)
    except Exception:
        return 0


def import_comments(target, platform):
    """导入指定监控目标的评论数据到 RawComment 表
    target: MonitorTarget 实例
    platform: 平台码（douyin/kuaishou/shipinhao/weibo/xhs/zhihu/tieba/bili）
    """
    # 转换平台码
    sys_platform = PLATFORM_MAP.get(platform, platform)
    if sys_platform not in PLATFORM_MAP.values():
        logger.error(f"Unsupported platform: {platform}")
        return {"success": False, "error": f"Unsupported platform: {platform}"}

    # 构建评论数据路径
    base_dir = MEDIACRAWLER_DIR / "data" / platform / "jsonl"
    if not base_dir.exists():
        logger.error(f"Comment data directory not found: {base_dir}")
        return {"success": False, "error": f"Comment data directory not found: {base_dir}"}

    # 查找评论文件（按日期命名的 jsonl 文件）
    comment_files = sorted(base_dir.glob("comments_*.jsonl"))
    if not comment_files:
        # 如果没有专门的评论文件，尝试从搜索内容文件中提取评论
        search_files = sorted(base_dir.glob("search_contents_*.jsonl"))
        if not search_files:
            logger.error(f"No comment or search files found in {base_dir}")
            return {"success": False, "error": f"No comment or search files found in {base_dir}"}
        comment_files = search_files

    imported = 0
    skipped = 0
    intent_scoring = IntentScoring()

    for comment_file in comment_files:
        logger.info(f"Processing comment file: {comment_file}")
        
        try:
            with open(comment_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        raw_data = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error at line {line_num}: {e}")
                        continue

                    # 根据目标类型提取不同的字段
                    if target.target_type == "video":
                        # 视频：提取 aweme_id 或 video_id 作为目标ID
                        target_id = raw_data.get("aweme_id") or raw_data.get("video_id") or raw_data.get("item_id")
                        # 评论ID：优先使用 comment_id，如果没有则使用唯一标识
                        comment_id = raw_data.get("comment_id") or f"{target_id}_{raw_data.get('user_id', '')}_{line_num}"
                        
                        # 评论内容
                        content = raw_data.get("content") or raw_data.get("text") or ""
                        
                        # 用户信息
                        user_info = raw_data.get("user", {}) or {}
                        uid = user_info.get("id") or user_info.get("uid") or user_info.get("user_id") or ""
                        nickname = user_info.get("nickname") or user_info.get("name") or ""
                        avatar_url = user_info.get("avatar_url") or user_info.get("avatar") or ""
                        fan_cnt = _int_or_zero(user_info.get("follower_count") or user_info.get("fans_count") or 0)
                        region = user_info.get("region") or ""
                        
                        # 评论统计
                        like_count = _int_or_zero(raw_data.get("like_count") or raw_data.get("digg_count") or 0)
                        reply_count = _int_or_zero(raw_data.get("reply_count") or raw_data.get("child_comment_count") or 0)
                        parent_comment_id = raw_data.get("parent_comment_id") or ""
                        
                        # 评论时间
                        comment_time = _parse_time(raw_data.get("create_time") or raw_data.get("timestamp"))

                    elif target.target_type == "live_room":
                        # 直播间：提取 room_id 作为目标ID
                        target_id = raw_data.get("room_id") or raw_data.get("live_id")
                        comment_id = raw_data.get("comment_id") or f"{target_id}_{raw_data.get('user_id', '')}_{line_num}"
                        
                        content = raw_data.get("content") or raw_data.get("text") or ""
                        
                        user_info = raw_data.get("user", {}) or {}
                        uid = user_info.get("id") or user_info.get("uid") or ""
                        nickname = user_info.get("nickname") or user_info.get("name") or ""
                        avatar_url = user_info.get("avatar_url") or user_info.get("avatar") or ""
                        fan_cnt = _int_or_zero(user_info.get("follower_count") or user_info.get("fans_count") or 0)
                        region = user_info.get("region") or ""
                        
                        like_count = _int_or_zero(raw_data.get("like_count") or 0)
                        reply_count = _int_or_zero(raw_data.get("reply_count") or 0)
                        parent_comment_id = raw_data.get("parent_comment_id") or ""
                        
                        comment_time = _parse_time(raw_data.get("create_time") or raw_data.get("timestamp"))

                    elif target.target_type == "competitor_account":
                        # 竞品账号：提取 creator_hash 或 user_id 作为目标ID
                        target_id = raw_data.get("creator_hash") or raw_data.get("user_id") or raw_data.get("author_id")
                        comment_id = raw_data.get("comment_id") or f"{target_id}_{raw_data.get('user_id', '')}_{line_num}"
                        
                        content = raw_data.get("content") or raw_data.get("text") or ""
                        
                        user_info = raw_data.get("user", {}) or {}
                        uid = user_info.get("id") or user_info.get("uid") or ""
                        nickname = user_info.get("nickname") or user_info.get("name") or ""
                        avatar_url = user_info.get("avatar_url") or user_info.get("avatar") or ""
                        fan_cnt = _int_or_zero(user_info.get("follower_count") or user_info.get("fans_count") or 0)
                        region = user_info.get("region") or ""
                        
                        like_count = _int_or_zero(raw_data.get("like_count") or 0)
                        reply_count = _int_or_zero(raw_data.get("reply_count") or 0)
                        parent_comment_id = raw_data.get("parent_comment_id") or ""
                        
                        comment_time = _parse_time(raw_data.get("create_time") or raw_data.get("timestamp"))

                    else:
                        logger.warning(f"Unknown target type: {target.target_type}")
                        continue

                    # 检查目标是否匹配（如果是竞品账号，需要检查目标ID是否匹配）
                    if target.target_type == "competitor_account" and target.target_id != target_id:
                        continue

                    # 去重：按 platform + comment_id 检查是否已存在
                    existing_comment = RawComment.objects.filter(
                        platform=sys_platform,
                        comment_id=comment_id
                    ).first()
                    
                    if existing_comment:
                        # 更新现有评论的统计信息（如果需要）
                        changed = False
                        if existing_comment.like_count != like_count:
                            existing_comment.like_count = like_count
                            changed = True
                        if existing_comment.reply_count != reply_count:
                            existing_comment.reply_count = reply_count
                            changed = True
                        if existing_comment.comment_time != comment_time:
                            existing_comment.comment_time = comment_time
                            changed = True
                        
                        if changed:
                            existing_comment.save()
                        skipped += 1
                        continue

                    # 创建新评论
                    comment = RawComment.objects.create(
                        target=target,
                        platform=sys_platform,
                        comment_id=comment_id,
                        uid=uid,
                        nickname=nickname,
                        avatar_url=avatar_url,
                        fan_cnt=fan_cnt,
                        region=region,
                        content=content,
                        like_count=like_count,
                        reply_count=reply_count,
                        parent_comment_id=parent_comment_id,
                        comment_time=comment_time,
                    )

                    # 进行意图识别
                    try:
                        intent_score, breakdown = intent_scoring.score({"content": content}, [target.title or ""])
                        
                        # 确定意图级别
                        if intent_score >= 70:
                            level = "llm_pass"
                        elif intent_score >= 50:
                            level = "nlp_pass"
                        else:
                            level = "kw_only"

                        IntentComment.objects.create(
                            raw_comment=comment,
                            intent_score=intent_score,
                            hit_keyword="",  # 可以根据实际需求添加关键词匹配逻辑
                            level=level,
                            is_ad=False,  # 默认不是广告/同行
                            is_converted=False,  # 默认未转化
                            llm_raw=breakdown,
                        )
                        
                        imported += 1
                        
                    except Exception as e:
                        logger.error(f"Intent scoring failed for comment {comment_id}: {e}")
                        # 即使意图识别失败，也要保存评论
                        imported += 1

        except Exception as e:
            logger.error(f"Error processing file {comment_file}: {e}")
            continue

    # 更新目标的上次拉取时间
    target.last_pull_time = datetime.now()
    target.save()

    logger.info(f"Comment import completed: imported={imported}, skipped={skipped}")
    return {
        "success": True,
        "platform": sys_platform,
        "imported": imported,
        "skipped": skipped,
        "files": [f.name for f in comment_files],
    }


def convert_to_lead(comment):
    """将评论用户转为线索
    comment: RawComment 实例
    """
    from apps.leads.models import Lead
    
    # 检查是否已经存在相同的线索（按用户+平台+目标ID）
    existing_lead = Lead.objects.filter(
        platform=comment.platform,
        author_id=comment.uid
    ).first()
    
    if existing_lead:
        # 更新现有线索的统计信息
        changed = False
        if existing_lead.like_count != comment.like_count:
            existing_lead.like_count = comment.like_count
            changed = True
        if existing_lead.comment_count != comment.reply_count:
            existing_lead.comment_count = comment.reply_count
            changed = True
        
        if changed:
            existing_lead.save()
        return {"success": True, "lead_id": existing_lead.id, "action": "updated"}

    # 获取意图识别结果
    intent_comment = comment.intent.first()
    intent_score = intent_comment.intent_score if intent_comment else 0
    intent_label = "none"
    
    if intent_comment:
        if intent_score >= 70:
            intent_label = "high"
        elif intent_score >= 50:
            intent_label = "medium"
        elif intent_score >= 30:
            intent_label = "low"

    # 创建新线索
    lead = Lead.objects.create(
        user=comment.target.created_by,
        platform=comment.platform,
        item_id=comment.target.target_id,  # 使用目标ID作为内容ID
        title=comment.target.title or f"{comment.nickname}的评论",
        content=comment.content,
        author=comment.nickname,
        author_id=comment.uid,
        url=comment.target.get_absolute_url() if hasattr(comment.target, 'get_absolute_url') else "",
        like_count=comment.like_count,
        comment_count=comment.reply_count,
        publish_time=comment.comment_time,
        region=comment.region,
        demand="",  # 可以根据实际需求添加需求识别
        intent_label=intent_label,
        intent_score=intent_score,
        score_breakdown={} if intent_comment else intent_comment.llm_raw if intent_comment else {},
        tags=[PLATFORM_NAMES.get(comment.platform, comment.platform), "评论线索"],
        status="new",
        note=f"来源：{comment.target.title} 的评论",
    )

    # 标记评论已转化
    if intent_comment:
        intent_comment.is_converted = True
        intent_comment.save()

    return {"success": True, "lead_id": lead.id, "action": "created"}