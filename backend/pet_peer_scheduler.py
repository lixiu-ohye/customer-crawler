# -*- coding: utf-8 -*-
"""
宠物同行评论区获客调度器

核心链路（用户需求：抓同行评论区 → 联想筛选有需求的用户）：
  同行内容搜索（宠物医院/宠物店/宠物博主 关键词）→ MediaCrawler 抓主帖+评论区
  → 宠物需求识别（实体词+需求词）→ GLM 深度筛选（第一人称真实需求）
  → 评论用户入库 Lead（is_customer=True 才显示为"客户"）

用法：
  python pet_peer_scheduler.py --rounds 3     # 跑 3 轮（每轮多个平台×关键词）
  python pet_peer_scheduler.py --glm-only     # 只补跑 GLM 筛选
  python pet_peer_scheduler.py --once         # 单轮后退出
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import django

BACKEND_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BACKEND_DIR.parent.parent
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"
STATE_FILE = BACKEND_DIR / ".pet_peer_state.json"

sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.crawler.services.customer_ai_filter import CustomerAIFilter
from apps.leads.models import Lead

PYTHON = sys.executable
SCAN_SCRIPT = BACKEND_DIR / "pet_scan_comments.py"

# ============ 同行内容池（宠物行业） ============
# 这些关键词搜出来的是宠物行业同行的热门内容（宠物医院/宠物店/宠物博主/宠物KOL）
# 他们的评论区 = 潜在客户聚集地
PET_PEER_QUERIES = [
    # 宠物医疗同行
    "宠物医院 猫咪 看病", "宠物医院 狗狗 治疗", "宠物绝育 多少钱",
    "宠物疫苗 价格", "宠物驱虫 怎么办", "猫咪 呕吐 怎么办",
    # 宠物服务同行
    "宠物店 洗澡 多少钱", "宠物美容 造型", "宠物寄养 多少钱",
    "宠物托运 价格", "宠物上门喂养",
    # 宠物博主/KOL 热门内容
    "猫咪 日常 分享", "狗狗 训练 教程", "养猫 新手 攻略",
    "宠物 生病 经验", "猫粮 推荐 测评", "狗粮 推荐 测评",
    # 直接需求型
    "附近 宠物医院", "宠物医院 推荐", "宠物店 推荐", "猫咪 生病 求助",
]

# 平台轮转（抖音搜索易风控，先用能稳定出数据的平台：微博/知乎/贴吧；小红书待 cookie 验证）
# 用户核心需求平台是抖音/小红书，但搜索接口被风控时先保数据量，后续 cookie 修复后再加回
PLATFORM_CODE = {"weibo": "wb", "zhihu": "zhihu", "tieba": "tieba", "xiaohongshu": "xhs"}

NOTES_PER_KEYWORD = 5   # 每个关键词抓多少条内容
MAX_COMMENTS = 50       # 每条内容抓多少评论
KEYWORD_TIMEOUT = 180   # 单关键词超时（秒）
INTERVAL = 30           # 关键词间间隔（秒）


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"round": 0, "idx": 0, "last_run": None, "total_crawl": 0}


def save_state(st):
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def run_keyword_crawl(platform, keyword):
    """跑单个关键词：搜索同行内容 + 抓评论"""
    code = PLATFORM_CODE[platform]
    cmd = [
        PYTHON, str(MEDIACRAWLER_DIR / "main.py"),
        "--platform", code,
        "--lt", "cookie",
        "--type", "search",
        "--keywords", keyword,
        "--crawler_max_notes_count", str(NOTES_PER_KEYWORD),
        "--headless", "true",
        "--save_data_option", "jsonl",
        "--get_comment", "true",
        "--max_comments_count_singlenotes", str(MAX_COMMENTS),
    ]
    print(f"[宠物同行] {platform} 关键词: {keyword}")
    try:
        proc = subprocess.run(
            cmd, cwd=str(MEDIACRAWLER_DIR),
            capture_output=True, text=True, timeout=KEYWORD_TIMEOUT,
            encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if proc.returncode != 0:
            print(f"  rc={proc.returncode} stderr: {proc.stderr[-200:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  timeout")
        return False
    except Exception as e:
        print(f"  error: {e}")
        return False


def run_scan(days=2, glm_limit=None):
    """扫描评论入库 + GLM 筛选"""
    print("[宠物同行] 扫描评论入库 + GLM 筛选...")
    args = [PYTHON, str(SCAN_SCRIPT), "--days", str(days)]
    if glm_limit:
        args += ["--limit", str(glm_limit)]
    proc = subprocess.run(
        args, cwd=str(BACKEND_DIR),
        capture_output=True, text=True, timeout=1800,
        encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    print(proc.stdout[-500:] if proc.stdout else "")
    if proc.returncode != 0 and proc.stderr:
        print(f"scan stderr: {proc.stderr[-300:]}")
    return proc.returncode == 0


def stats():
    """统计宠物线索"""
    all_leads = list(Lead.objects.all())
    pet = [l for l in all_leads if l.tags and any("宠物" in str(t) for t in l.tags)]
    cust = sum(1 for l in pet if l.is_customer is True)
    return len(pet), cust


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--glm-only", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--scan-only", action="store_true")
    args = parser.parse_args()

    st = load_state()

    if args.glm_only:
        print("[宠物同行] GLM 补筛模式")
        run_scan(days=7, glm_limit=None)
        p, c = stats()
        print(f"[宠物同行] 完成: 宠物线索 {p}, 客户 {c}")
        return

    if args.scan_only:
        run_scan(days=2)
        p, c = stats()
        print(f"[宠物同行] 完成: 宠物线索 {p}, 客户 {c}")
        return

    rounds = args.rounds if not args.once else 1
    for r in range(rounds):
        st["round"] += 1
        print(f"\n========== 第 {st['round']} 轮 ==========")
        for platform in ["weibo", "zhihu", "tieba", "xiaohongshu"]:
            for kw in PET_PEER_QUERIES:
                ok = run_keyword_crawl(platform, kw)
                st["total_crawl"] += 1
                st["last_run"] = datetime.now().isoformat()
                save_state(st)
                time.sleep(INTERVAL)
        # 每轮结束扫描入库 + GLM 筛选
        run_scan(days=2)
        p, c = stats()
        print(f"[宠物同行] 第 {st['round']} 轮完成: 宠物线索 {p}, 客户 {c}")
        save_state(st)
        if args.once:
            break


if __name__ == "__main__":
    main()
