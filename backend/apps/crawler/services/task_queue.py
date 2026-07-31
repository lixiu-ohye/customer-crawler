"""任务队列：Redis + 多线程队列、任务进度统计、停止/续跑"""
import json
import threading
import time
import uuid
from datetime import datetime

try:
    import redis as redis_lib

    REDIS_OK = True
except ImportError:
    REDIS_OK = False


class TaskQueue:
    """进程内 + Redis 双模任务队列"""

    def __init__(self, redis_url=None, task_store=None):
        self.task_store = task_store  # 可选：Django ORM 任务模型存取器
        self._redis = None
        if REDIS_OK and redis_url:
            try:
                self._redis = redis_lib.from_url(redis_url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None
        self._lock = threading.Lock()
        self._tasks = {}  # task_id -> task dict
        self._threads = {}  # task_id -> thread
        self._stop_flags = {}  # task_id -> Event

    def create_task(self, task_id=None, **fields):
        """创建任务记录"""
        task = {
            "id": task_id or uuid.uuid4().hex[:12],
            "status": "pending",  # pending/running/paused/completed/failed/stopped
            "progress": 0,
            "total": 0,
            "processed": 0,
            "found": 0,
            "message": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": None,
            "finished_at": None,
            **fields,
        }
        with self._lock:
            self._tasks[task["id"]] = task
        if self._redis:
            self._redis.hset("crawler:tasks", task["id"], json.dumps(task, ensure_ascii=False))
        return task

    def update_progress(self, task_id, processed=None, found=None, total=None, message=None, progress=None):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            if processed is not None:
                task["processed"] = processed
            if found is not None:
                task["found"] = found
            if total is not None:
                task["total"] = total
            if message is not None:
                task["message"] = message
            if progress is not None:
                task["progress"] = progress
            elif task.get("total"):
                task["progress"] = min(100, int(task["processed"] / task["total"] * 100))
        if self._redis:
            self._redis.hset("crawler:tasks", task_id, json.dumps(task, ensure_ascii=False))

    def set_status(self, task_id, status, message=None):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task["status"] = status
            if message:
                task["message"] = message
            if status in ("completed", "failed", "stopped"):
                task["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status == "running" and not task["started_at"]:
                task["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self._redis:
            self._redis.hset("crawler:tasks", task_id, json.dumps(task, ensure_ascii=False))

    def get_task(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
        if task:
            return task
        if self._redis:
            raw = self._redis.hget("crawler:tasks", task_id)
            if raw:
                return json.loads(raw)
        return None

    def list_tasks(self, status=None, limit=100):
        with self._lock:
            tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks[:limit]

    def stop(self, task_id):
        """请求停止：置停止标记，正在跑的线程在检查点退出"""
        with self._lock:
            flag = self._stop_flags.get(task_id)
        if flag:
            flag.set()
            self.set_status(task_id, "stopped", "已停止")
            return True
        task = self.get_task(task_id)
        if task and task["status"] in ("pending", "running"):
            self.set_status(task_id, "stopped", "已停止")
            return True
        return False

    def pause(self, task_id):
        """暂停：仅标记（线程内通过检查点挂起）"""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task["status"] == "running":
                task["status"] = "paused"
                return True
        return False

    def resume(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task["status"] == "paused":
                task["status"] = "running"
                return True
        return False

    def is_stop_requested(self, task_id):
        flag = self._stop_flags.get(task_id)
        return bool(flag and flag.is_set())

    def register_stop_flag(self, task_id):
        flag = threading.Event()
        with self._lock:
            self._stop_flags[task_id] = flag
        return flag

    def run_async(self, task_id, fn, *args, **kwargs):
        """在线程中执行 fn，自动维护任务状态"""
        flag = self.register_stop_flag(task_id)
        self.set_status(task_id, "running")

        def runner():
            try:
                fn(*args, task_id=task_id, stop_flag=flag, **kwargs)
                if not self.is_stop_requested(task_id):
                    self.set_status(task_id, "completed", "采集完成")
            except Exception as exc:
                self.set_status(task_id, "failed", str(exc))

        t = threading.Thread(target=runner, daemon=True)
        with self._lock:
            self._threads[task_id] = t
        t.start()
        return t
