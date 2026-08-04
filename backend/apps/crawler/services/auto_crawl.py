# -*- coding: utf-8 -*-
"""后台自动批量采集服务
无人值守：扫描 12 行业词库 → 逐关键词调 MediaCrawler CLI（复用登录态）→ 自动导入线索库
设计为常驻后台线程/独立进程运行，用户无感知。

用法:
    独立进程: python auto_crawl.py
"""
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import django

logger = logging.getLogger("auto_crawl")

# 路径（services -> crawler -> apps -> backend -> customer-crawler -> workspace）
# auto_crawl.py 位于 backend/apps/crawler/services/
FILE_PARENT = Path(__file__).resolve().parent
# parents[0]=crawler [1]=apps [2]=backend [3]=customer-crawler [4]=workspace
BACKEND_DIR = FILE_PARENT.parents[2]
CUSTOMER_DIR = FILE_PARENT.parents[3]
WORKSPACE_DIR = FILE_PARENT.parents[4]
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"

# 确保 backend 目录在 sys.path（Django settings 模块 config.settings）
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# 关键词轮询游标（内存 + 文件持久化，重启续跑）
STATE_FILE = BACKEND_DIR / ".auto_crawl_state.json"

# 每关键词采集条数上限（合规合理频率，避免过度抓取）
NOTES_PER_KEYWORD = 10
# 串行间隔（秒）
CRAWL_INTERVAL = 15
# 单关键词超时（秒）
KEYWORD_TIMEOUT = 240

# CLI 平台码 -> 输出目录平台名
PLATFORM_NAME_MAP = {
    "wb": "weibo",
    "dy": "douyin",
    "xhs": "xiaohongshu",
    "ks": "kuaishou",
    "tieba": "tieba",
    "zhihu": "zhihu",
    "bili": "bilibili",
}


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"cursor": 0, "last_run": None, "total_imported": 0}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def import_jsonl_to_leads(jsonl_path, platform="weibo"):
    """调用 Django 的 jsonl_importer 导入线索库（import_jsonl 从目录读取全部 jsonl）"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from django.contrib.auth import get_user_model
    from apps.crawler.services.jsonl_importer import import_jsonl
    try:
        user = get_user_model().objects.filter(is_superuser=True).first()
        if not user:
            user = get_user_model().objects.first()
        if not user:
            return {"imported": 0, "error": "no user found"}
        result = import_jsonl(user, platform=platform)
        return result
    except Exception as e:
        logger.error(f"import failed: {e}")
        return {"imported": 0, "error": str(e)}


def run_keyword(keyword, platform="wb", max_notes=NOTES_PER_KEYWORD):
    """跑单个关键词采集（MediaCrawler CLI），返回新增 jsonl 文件路径列表
    实际输出目录: data/{platform_name}/jsonl，platform_name 为完整名（weibo 等）
    """
    platform_name = PLATFORM_NAME_MAP.get(platform, platform)
    out_dir = MEDIACRAWLER_DIR / "data" / platform_name / "jsonl"
    # 记录采集前已有文件（去重新增）
    before = set(out_dir.glob("*.jsonl")) if out_dir.exists() else set()

    cmd = [
        sys.executable, str(MEDIACRAWLER_DIR / "main.py"),
        "--platform", platform,
        "--lt", "cookie",
        "--type", "search",
        "--keywords", keyword,
        "--crawler_max_notes_count", str(max_notes),
        "--headless", "true",
        "--save_data_option", "jsonl",
        "--get_comment", "true",  # 搜索时顺带抓评论（评论区获客数据源）
    ]
    logger.info(f"[auto_crawl] RUN: {keyword} ({platform})")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(MEDIACRAWLER_DIR),
            capture_output=True,
            text=True,
            timeout=KEYWORD_TIMEOUT,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        logger.info(f"[auto_crawl] done rc={proc.returncode} keyword={keyword}")
        if proc.returncode != 0:
            logger.warning(f"stderr tail: {proc.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        logger.warning(f"[auto_crawl] timeout keyword={keyword}")

    # 找新增 jsonl
    now = set(out_dir.glob("*.jsonl")) if out_dir.exists() else set()
    new_files = sorted(now - before, key=lambda p: p.stat().st_mtime, reverse=True)
    return new_files


def build_queue():
    """构建关键词队列：12 行业主词+长尾词，过滤否定词，去重
    支持环境变量限制：
      AUTO_CRAWL_MAX_ITEMS: 最多跑多少个关键词（测试用）
      AUTO_CRAWL_PLATFORM: 平台码（默认 wb）
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from apps.keywords.industry_library import INDUSTRY_LIBRARY, all_words, all_negative_words

    queue = []
    seen = set()
    for industry, lib in INDUSTRY_LIBRARY.items():
        for w in all_words(industry):
            if w in seen:
                continue
            seen.add(w)
            negs = all_negative_words(industry)
            if any(n and n in w for n in negs):
                continue
            queue.append({"keyword": w, "industry": industry})

    max_items = int(os.environ.get("AUTO_CRAWL_MAX_ITEMS", "0") or "0")
    if max_items > 0:
        queue = queue[:max_items]
    return queue


def get_platforms():
    """读取平台列表（环境变量 AUTO_CRAWL_PLATFORMS，逗号分隔；默认 6 平台）"""
    default = ["wb", "dy", "xhs", "ks", "zhihu", "tieba"]
    env = os.environ.get("AUTO_CRAWL_PLATFORMS", "")
    if env:
        return [p.strip() for p in env.split(",") if p.strip()]
    return default


def auto_crawl_loop():
    """主循环：多平台轮转 — 每轮选一个平台跑完词库，下一轮换平台
    每个平台独立 cursor（state 里 cursor_<platform>），平台间互不影响
    """
    state = load_state()
    queue = build_queue()
    platforms = get_platforms()
    if not queue:
        return

    # 平台轮转：上一轮跑的平台 +1
    cur_idx = state.get("platform_idx", 0) % len(platforms)
    platform = platforms[cur_idx]
    platform_name = PLATFORM_NAME_MAP.get(platform, platform)
    state["platform_idx"] = (cur_idx + 1) % len(platforms)
    save_state(state)
    logger.info(f"[auto_crawl] this round platform={platform} ({platform_name}), platforms={platforms}")

    cursor_key = "cursor_" + platform
    cursor = state.get(cursor_key, 0)
    if cursor >= len(queue):
        cursor = 0  # 该平台一轮完成，从头再来

    for i in range(cursor, len(queue)):
        item = queue[i]
        state[cursor_key] = i
        state["last_run"] = datetime.now().isoformat()
        save_state(state)

        logger.info(f"[auto_crawl] [{i + 1}/{len(queue)}] platform={platform} industry={item['industry']} keyword={item['keyword']}")
        try:
            run_keyword(item["keyword"], platform=platform)
            # MediaCrawler 按日期追加同名 jsonl，无法用“新增文件”判断；
            # 直接导入该平台全量 jsonl（import_jsonl 内部按 item_id 去重 + upsert 补标签，幂等安全）
            result = import_jsonl_to_leads(None, platform=platform_name)
            n = result.get("imported", 0)
            state["total_imported"] += n
            logger.info(f"[auto_crawl] import result: imported={n} skipped={result.get('skipped_dup')} (total={state['total_imported']})")
            save_state(state)
        except Exception as e:
            logger.exception(f"keyword failed: {platform}/{item['keyword']}: {e}")

        # 串行间隔 + 避免密集请求
        time.sleep(CRAWL_INTERVAL)

    state[cursor_key] = 0
    save_state(state)
    logger.info(f"[auto_crawl] round done for {platform}, reset cursor. Next round: {platforms[state.get('platform_idx', 0) % len(platforms)]}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BACKEND_DIR / "auto_crawl.log", encoding="utf-8"),
        ],
    )
    while True:
        try:
            auto_crawl_loop()
        except Exception as e:
            logger.exception("loop error")
        logger.info("[auto_crawl] next round in 60s...")
        time.sleep(60)
