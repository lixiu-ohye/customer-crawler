# -*- coding: utf-8 -*-
"""宠物行业专项评论采集：搜索宠物同行内容并抓评论区"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BACKEND_DIR.parent.parent
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"

PYTHON = sys.executable

# 宠物同行热门内容搜索词（搜出来的是宠物店/宠物医院/宠物博主的视频/笔记 → 评论区就是潜在客户）
PET_PEER_QUERIES = [
    # 宠物服务同行（他们的评论区有客户在咨询）
    "宠物医院 看病", "宠物店 洗澡", "宠物美容 造型", "宠物寄养 多少钱",
    "宠物绝育 价格", "宠物疫苗 多少钱", "宠物驱虫 怎么",
    # 宠物博主热门内容（评论区大量宠物主人在交流）
    "猫咪 日常", "狗狗 训练", "宠物 生病 怎么办", "猫粮 推荐", "狗粮 推荐",
    # 直接需求
    "宠物托运", "宠物上门喂养", "宠物摄影", "宠物殡葬",
]

# 平台轮转
PLATFORMS = ["douyin", "xiaohongshu", "weibo", "tieba"]

def run_crawl(platform, keyword):
    """跑一轮指定关键词搜索 + 评论采集"""
    code = {"douyin": "dy", "xiaohongshu": "xhs", "weibo": "wb", "tieba": "tieba"}[platform]
    cmd = [
        PYTHON, str(MEDIACRAWLER_DIR / "main.py"),
        "--platform", code,
        "--lt", "cookie",
        "--type", "search",
        "--keywords", keyword,
        "--crawler_max_notes_count", "5",
        "--headless", "true",
        "--save_data_option", "jsonl",
        "--get_comment", "true",
        "--max_comments_count_singlenotes", "50",
    ]
    print(f"[宠物采集] {platform} 关键词: {keyword}")
    try:
        proc = subprocess.run(
            cmd, cwd=str(MEDIACRAWLER_DIR),
            capture_output=True, text=True, timeout=600,
            encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        print(f"  returncode: {proc.returncode}")
        if proc.returncode != 0:
            print(f"  stderr tail: {proc.stderr[-300:]}")
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        print("  timeout")
        return False
    except Exception as e:
        print(f"  error: {e}")
        return False


def main():
    # 只跑抖音和小红书（用户核心需求平台）
    targets = []
    for kw in PET_PEER_QUERIES:
        for plat in ["douyin", "xiaohongshu"]:
            targets.append((plat, kw))
    
    # 交错轮转
    print(f"[宠物采集] 共 {len(targets)} 个任务")
    ok = 0
    for i, (plat, kw) in enumerate(targets):
        if run_crawl(plat, kw):
            ok += 1
        time.sleep(5)
    print(f"[宠物采集] 完成 {ok}/{len(targets)}")


if __name__ == "__main__":
    main()
