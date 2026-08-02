# -*- coding: utf-8 -*-
"""评论采集启动器
调用 MediaCrawler CLI 抓取指定视频/账号的评论，支持后台线程运行
"""
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import django

logger = logging.getLogger("comment_crawler")

# 路径配置
BACKEND_DIR = Path(__file__).resolve().parents[3]  # backend
WORKSPACE_DIR = BACKEND_DIR.parents[1]  # workspace
MEDIACRAWLER_DIR = WORKSPACE_DIR / "MediaCrawler"

# 确保 Django 设置
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 平台映射
PLATFORM_NAME_MAP = {
    "douyin": "dy",
    "kuaishou": "ks", 
    "xiaohongshu": "xhs",
    "weibo": "wb",
    "zhihu": "zhihu",
    "tieba": "tieba",
    "bilibili": "bili",
}

# 平台支持评论采集的配置
COMMENT_CONFIGS = {
    "douyin": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"  # 使用详情模式获取评论
    },
    "kuaishou": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    },
    "xiaohongshu": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    },
    "weibo": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    },
    "zhihu": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    },
    "tieba": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    },
    "bilibili": {
        "enable_comments": True,
        "max_comments": 100,
        "type": "detail"
    }
}


class CommentCrawlerThread(threading.Thread):
    """评论采集后台线程"""
    
    def __init__(self, target, platform):
        super().__init__()
        self.target = target
        self.platform = platform
        self.platform_code = PLATFORM_NAME_MAP.get(platform, platform)
        self.config = COMMENT_CONFIGS.get(platform, {})
        self.daemon = True
        self._stop_event = threading.Event()
        
    def stop(self):
        """停止线程"""
        self._stop_event.set()
        
    def run(self):
        """执行评论采集"""
        try:
            logger.info(f"[CommentCrawler] Starting crawl for target {self.target.id} ({self.platform})")
            
            # 更新目标状态为监控中
            self.target.monitor_status = "active"
            self.target.save()
            
            # 执行评论采集
            result = self._run_comment_crawl()
            
            if result["success"]:
                logger.info(f"[CommentCrawler] Crawl completed for target {self.target.id}: {result}")
            else:
                logger.error(f"[CommentCrawler] Crawl failed for target {self.target.id}: {result['error']}")
                
        except Exception as e:
            logger.error(f"[CommentCrawler] Error in crawl thread for target {self.target.id}: {e}")
            # 更新目标状态为已停止
            self.target.monitor_status = "stopped"
            self.target.save()
            
    def _run_comment_crawl(self):
        """执行实际的评论采集"""
        # 构造 MediaCrawler CLI 命令
        cmd = self._build_crawl_command()
        
        logger.info(f"[CommentCrawler] Running command: {' '.join(cmd)}")
        
        try:
            # 执行命令
            proc = subprocess.run(
                cmd,
                cwd=str(MEDIACRAWLER_DIR),
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            
            logger.info(f"[CommentCrawler] Command completed with return code: {proc.returncode}")
            
            if proc.returncode != 0:
                logger.warning(f"[CommentCrawler] stderr: {proc.stderr[-500:]}")
                return {"success": False, "error": f"Command failed with code {proc.returncode}: {proc.stderr}"}
            
            # 检查是否有输出文件
            output_files = self._check_output_files()
            if not output_files:
                return {"success": False, "error": "No output files generated"}
            
            logger.info(f"[CommentCrawler] Generated files: {output_files}")
            return {"success": True, "output_files": output_files}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_crawl_command(self):
        """构造 MediaCrawler CLI 命令"""
        cmd = [
            sys.executable, str(MEDIACRAWLER_DIR / "main.py"),
            "--platform", self.platform_code,
            "--lt", "cookie",  # 使用cookie登录
            "--type", self.config.get("type", "detail"),
            "--headless", "true",
            "--save_data_option", "jsonl",
            "--get_comment", "true",  # 启用评论采集
        ]
        
        # 根据目标类型添加不同的参数
        if self.target.target_type == "video":
            # 视频：使用视频ID
            if self.platform == "douyin":
                cmd.extend(["--specified_id", self.target.target_id])
            elif self.platform == "weibo":
                cmd.extend(["--specified_id", self.target.target_id])
            elif self.platform == "bilibili":
                cmd.extend(["--specified_id", self.target.target_id])
            else:
                # 其他平台使用通用方式
                cmd.extend(["--specified_id", self.target.target_id])
                
        elif self.target.target_type == "live_room":
            # 直播间：使用直播间ID
            cmd.extend(["--specified_id", self.target.target_id])
            
        elif self.target.target_type == "competitor_account":
            # 竞品账号：使用创作者ID
            if self.platform == "douyin":
                cmd.extend(["--creator_id", self.target.target_id])
            elif self.platform == "xiaohongshu":
                cmd.extend(["--creator_id", self.target.target_id])
            elif self.platform == "weibo":
                cmd.extend(["--creator_id", self.target.target_id])
            else:
                cmd.extend(["--creator_id", self.target.target_id])
        
        # 设置评论数量限制
        if self.config.get("enable_comments"):
            cmd.extend(["--max_comments_count_singlenotes", str(self.config.get("max_comments", 100))])
        
        # 添加cookie（如果配置了）
        if hasattr(self.target, 'cookie') and self.target.cookie:
            cmd.extend(["--cookies", self.target.cookie])
        
        return cmd
    
    def _check_output_files(self):
        """检查输出文件"""
        platform_code = PLATFORM_NAME_MAP.get(self.platform, self.platform)
        output_dir = MEDIACRAWLER_DIR / "data" / platform_code / "jsonl"
        
        if not output_dir.exists():
            return []
        
        # 查找评论文件或相关文件
        comment_files = []
        
        # 查找评论文件
        comment_patterns = ["comments_*.jsonl", "search_contents_*.jsonl"]
        for pattern in comment_patterns:
            comment_files.extend(sorted(output_dir.glob(pattern)))
        
        # 只返回最近修改的文件（避免重复处理旧文件）
        if comment_files:
            comment_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(f) for f in comment_files[:5]]  # 最多返回5个最新文件
        
        return []


def start_comment_crawl(target):
    """启动评论采集（后台线程）
    target: MonitorTarget 实例
    """
    # 检查目标是否已经在运行
    if target.monitor_status == "active":
        logger.warning(f"Target {target.id} is already active")
        return {"success": False, "error": "Target is already active"}
    
    # 检查平台是否支持评论采集
    if target.platform not in COMMENT_CONFIGS:
        logger.error(f"Platform {target.platform} does not support comment crawling")
        return {"success": False, "error": f"Platform {target.platform} does not support comment crawling"}
    
    # 创建并启动线程
    crawler_thread = CommentCrawlerThread(target, target.platform)
    crawler_thread.start()
    
    # 保存线程引用（可选，用于后续管理）
    if not hasattr(target, 'crawler_thread'):
        target.crawler_thread = []
    target.crawler_thread.append(crawler_thread)
    target.save()
    
    logger.info(f"Started comment crawl for target {target.id}")
    return {"success": True, "thread_id": crawler_thread.ident}


def stop_comment_crawl(target):
    """停止评论采集"""
    if hasattr(target, 'crawler_thread') and target.crawler_thread:
        for thread in target.crawler_thread:
            thread.stop()
            thread.join(timeout=10)  # 等待10秒
        target.crawler_thread = []
        target.monitor_status = "stopped"
        target.save()
        logger.info(f"Stopped comment crawl for target {target.id}")
        return {"success": True}
    else:
        logger.warning(f"No active crawl thread found for target {target.id}")
        return {"success": False, "error": "No active crawl thread"}


def get_crawl_status(target):
    """获取评论采集状态"""
    status = {
        "target_id": target.id,
        "monitor_status": target.monitor_status,
        "last_pull_time": target.last_pull_time,
        "pull_interval_min": target.pull_interval_min,
        "is_running": target.monitor_status == "active",
    }
    
    if hasattr(target, 'crawler_thread') and target.crawler_thread:
        status["active_threads"] = [t.ident for t in target.crawler_thread if t.is_alive()]
    
    return status


def schedule_periodic_crawl():
    """定时调度评论采集（定期检查所有活跃目标）"""
    import django
    django.setup()
    
    from apps.monitor.models import MonitorTarget
    
    while True:
        try:
            # 获取所有活跃的监控目标
            active_targets = MonitorTarget.objects.filter(monitor_status="active")
            
            for target in active_targets:
                # 检查是否到了采集时间
                if should_crawl_now(target):
                    logger.info(f"Scheduling crawl for target {target.id}")
                    start_comment_crawl(target)
            
            # 休眠一段时间（比如每5分钟检查一次）
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in periodic crawl scheduler: {e}")
            time.sleep(60)  # 出错时等待1分钟再试


def should_crawl_now(target):
    """检查是否应该进行采集"""
    if not target.last_pull_time:
        return True  # 从未采集过，立即采集
    
    # 计算距离上次采集的时间（分钟）
    time_since_last = (datetime.now() - target.last_pull_time).total_seconds() / 60
    
    # 如果超过了设置的间隔时间，就进行采集
    return time_since_last >= target.pull_interval_min


# 如果直接运行此脚本，启动定时调度
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(BACKEND_DIR / "comment_crawler.log", encoding="utf-8"),
        ],
    )
    
    logger.info("Starting comment crawler periodic scheduler...")
    schedule_periodic_crawl()