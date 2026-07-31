"""风控限速器：每平台最小间隔、每分钟请求数、封禁、指数退避重试"""
import threading
import time


class RateLimiter:
    """基于时间窗口的每平台限速器"""

    def __init__(self, min_interval=3.0, max_rpm=20, ban_cooldown=300):
        self.min_interval = min_interval  # 两次请求最小间隔（秒）
        self.max_rpm = max_rpm  # 每分钟最大请求数
        self.ban_cooldown = ban_cooldown  # 风控冷却时间（秒）
        self._lock = threading.Lock()
        self._last_request = {}  # platform -> timestamp
        self._request_times = {}  # platform -> [timestamps]
        self._banned_until = {}  # platform -> timestamp

    def wait_if_needed(self, platform):
        """按平台限速等待"""
        with self._lock:
            now = time.time()
            # 封禁检查
            banned_until = self._banned_until.get(platform, 0)
            if now < banned_until:
                wait = banned_until - now
                time.sleep(wait)
                return True
            # 最小间隔
            last = self._last_request.get(platform, 0)
            elapsed = now - last
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            # RPM 窗口
            times = [t for t in self._request_times.get(platform, []) if now - t < 60]
            if len(times) >= self.max_rpm:
                sleep_time = 60 - (now - times[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                times = [t for t in times if now - t + sleep_time < 60]
            times.append(time.time())
            self._request_times[platform] = times
            self._last_request[platform] = time.time()
        return False

    def mark_banned(self, platform, reason=""):
        """标记平台风控，进入冷却"""
        with self._lock:
            self._banned_until[platform] = time.time() + self.ban_cooldown
            self._request_times[platform] = []
            return self.ban_cooldown

    def reset(self, platform):
        with self._lock:
            self._banned_until.pop(platform, None)
            self._request_times[platform] = []


class RetryPolicy:
    """指数退避重试"""

    def __init__(self, max_retries=3, backoff=5.0):
        self.max_retries = max_retries
        self.backoff = backoff

    def should_retry(self, attempt, status_code=None, exception=None):
        """决定是否重试：网络异常 / 5xx / 429 可重试；4xx 业务错误不重试"""
        if attempt >= self.max_retries:
            return False
        if exception is not None:
            return True
        if status_code is None:
            return False
        if status_code == 429 or 500 <= status_code < 600:
            return True
        return False

    def sleep_before_retry(self, attempt):
        time.sleep(self.backoff * (2 ** attempt))
