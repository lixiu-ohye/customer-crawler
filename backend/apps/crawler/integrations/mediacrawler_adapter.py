# -*- coding: utf-8 -*-
"""
MediaCrawler 集成适配器
将 MediaCrawler 集成到 Django 后端，统一管理爬虫任务
"""
import json
import os
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# MediaCrawler 路径
MEDIACRAWLER_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "MediaCrawler"

# 任务状态
TASK_STATUS = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}


class MediaCrawlerTask:
    """爬虫任务类"""
    
    def __init__(self, task_id: str, platform: str, keyword: str, crawler_type: str = "search"):
        self.task_id = task_id
        self.platform = platform
        self.keyword = keyword
        self.crawler_type = crawler_type
        self.status = TASK_STATUS["PENDING"]
        self.start_time = None
        self.end_time = None
        self.result_count = 0
        self.error_message = None
        self.output_file = None
        self.process = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "platform": self.platform,
            "keyword": self.keyword,
            "crawler_type": self.crawler_type,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result_count": self.result_count,
            "error_message": self.error_message,
            "output_file": str(self.output_file) if self.output_file else None
        }


class MediaCrawlerAdapter:
    """MediaCrawler 适配器 - 管理爬虫任务的启动、监控和结果处理"""
    
    # 任务存储（内存中，生产环境应使用 Redis 或数据库）
    _tasks: Dict[str, MediaCrawlerTask] = {}
    _tasks_lock = threading.Lock()
    
    @classmethod
    def get_task(cls, task_id: str) -> Optional[MediaCrawlerTask]:
        """获取任务"""
        with cls._tasks_lock:
            return cls._tasks.get(task_id)
    
    @classmethod
    def create_task(cls, platform: str, keyword: str, crawler_type: str = "search") -> MediaCrawlerTask:
        """创建爬虫任务"""
        task_id = str(uuid.uuid4())[:8]
        task = MediaCrawlerTask(task_id, platform, keyword, crawler_type)
        
        with cls._tasks_lock:
            cls._tasks[task_id] = task
        
        return task
    
    @classmethod
    def start_task(cls, task_id: str) -> Dict[str, Any]:
        """启动爬虫任务"""
        task = cls.get_task(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        if task.status == TASK_STATUS["RUNNING"]:
            return {"success": False, "error": "Task is already running"}
        
        # 检查 MediaCrawler 目录
        if not MEDIACRAWLER_DIR.exists():
            return {
                "success": False, 
                "error": f"MediaCrawler not found at {MEDIACRAWLER_DIR}",
                "hint": "Please clone MediaCrawler to workspace root"
            }
        
        # 准备配置
        platform_map = {
            "douyin": "dy",
            "xiaohongshu": "xhs",
            "kuaishou": "ks",
            "weibo": "wb",
            "zhihu": "zhihu",
            "tieba": "tieba"
        }
        
        mc_platform = platform_map.get(task.platform, task.platform)
        
        # 创建临时配置文件
        config_content = f"""# -*- coding: utf-8 -*-
PLATFORM = "{mc_platform}"
KEYWORDS = "{task.keyword}"
LOGIN_TYPE = "qrcode"
CRAWLER_TYPE = "{task.crawler_type}"
ENABLE_IP_PROXY = False
HEADLESS = False
SAVE_LOGIN_STATE = True
ENABLE_CDP_MODE = True
CDP_CONNECT_EXISTING = True
AUTO_CLOSE_BROWSER = False
SAVE_DATA_OPTION = "jsonl"
CRAWLER_MAX_NOTES_COUNT = 20
CRAWLER_MAX_SLEEP_SEC = 2
ENABLE_GET_COMMENTS = False
ENABLE_GET_SUB_COMMENTS = False
"""
        
        # 写入配置
        config_file = MEDIACRAWLER_DIR / "config" / "base_config.py"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
        except Exception as e:
            return {"success": False, "error": f"Failed to write config: {e}"}
        
        # 设置输出目录
        output_dir = MEDIACRAWLER_DIR / "data" / "jsonl" / mc_platform / task.crawler_type
        output_dir.mkdir(parents=True, exist_ok=True)
        task.output_file = output_dir
        
        # 启动爬虫进程
        try:
            # 使用 subprocess 启动，保持 UTF-8 输出
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            process = subprocess.Popen(
                ["python", "main.py"],
                cwd=str(MEDIACRAWLER_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True  # Windows 需要
            )
            
            task.process = process
            task.status = TASK_STATUS["RUNNING"]
            task.start_time = datetime.now()
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=cls._monitor_task,
                args=(task_id,),
                daemon=True
            )
            monitor_thread.start()
            
            return {
                "success": True,
                "task": task.to_dict(),
                "message": f"Crawler started for {task.platform} with keyword '{task.keyword}'"
            }
            
        except Exception as e:
            task.status = TASK_STATUS["FAILED"]
            task.error_message = str(e)
            task.end_time = datetime.now()
            return {"success": False, "error": str(e)}
    
    @classmethod
    def _monitor_task(cls, task_id: str):
        """监控任务执行"""
        task = cls.get_task(task_id)
        if not task or not task.process:
            return
        
        # 等待进程结束
        try:
            stdout, stderr = task.process.communicate(timeout=300)  # 5分钟超时
            
            if task.process.returncode == 0:
                task.status = TASK_STATUS["COMPLETED"]
                # 统计结果数量
                if task.output_file and task.output_file.exists():
                    json_files = list(task.output_file.glob("*.jsonl"))
                    total_count = 0
                    for json_file in json_files:
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                total_count += sum(1 for _ in f)
                        except:
                            pass
                    task.result_count = total_count
            else:
                task.status = TASK_STATUS["FAILED"]
                task.error_message = stderr[:500] if stderr else "Unknown error"
                
        except subprocess.TimeoutExpired:
            task.process.kill()
            task.status = TASK_STATUS["FAILED"]
            task.error_message = "Task timeout (5 minutes)"
        except Exception as e:
            task.status = TASK_STATUS["FAILED"]
            task.error_message = str(e)
        finally:
            task.end_time = datetime.now()
    
    @classmethod
    def cancel_task(cls, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        task = cls.get_task(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        if task.status != TASK_STATUS["RUNNING"]:
            return {"success": False, "error": f"Task is not running (current: {task.status})"}
        
        if task.process:
            task.process.terminate()
            try:
                task.process.wait(timeout=5)
            except:
                task.process.kill()
        
        task.status = TASK_STATUS["CANCELLED"]
        task.end_time = datetime.now()
        
        return {"success": True, "task": task.to_dict()}
    
    @classmethod
    def get_task_result(cls, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        task = cls.get_task(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        results = []
        
        if task.output_file and task.output_file.exists():
            json_files = list(task.output_file.glob("*.jsonl"))
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                results.append(json.loads(line))
                            except:
                                pass
                except Exception as e:
                    pass
        
        return {
            "success": True,
            "task": task.to_dict(),
            "results": results[:100]  # 限制返回数量
        }
    
    @classmethod
    def list_tasks(cls, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出任务"""
        with cls._tasks_lock:
            tasks = list(cls._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return [t.to_dict() for t in sorted(tasks, key=lambda x: x.start_time or datetime.min, reverse=True)]


# 便捷函数
def start_crawler(platform: str, keyword: str, crawler_type: str = "search") -> Dict[str, Any]:
    """启动爬虫的便捷函数"""
    task = MediaCrawlerAdapter.create_task(platform, keyword, crawler_type)
    return MediaCrawlerAdapter.start_task(task.task_id)


def get_crawler_status(task_id: str) -> Dict[str, Any]:
    """获取爬虫状态"""
    task = MediaCrawlerAdapter.get_task(task_id)
    if not task:
        return {"success": False, "error": "Task not found"}
    return {"success": True, "task": task.to_dict()}


def get_crawler_results(task_id: str) -> Dict[str, Any]:
    """获取爬虫结果"""
    return MediaCrawlerAdapter.get_task_result(task_id)