"""请求封装：各平台专属请求头、Cookie、CSRF token 生成、响应校验"""
import random
import time

import requests
from bs4 import BeautifulSoup

from .rate_limiter import RateLimiter, RetryPolicy

# 各平台模拟浏览器 UA 池
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
]

PLATFORM_HEADERS = {
    "douyin": {
        "referer": "https://www.douyin.com/",
        "accept": "application/json, text/plain, */*",
        "x-requested-with": "XMLHttpRequest",
    },
    "xiaohongshu": {
        "referer": "https://www.xiaohongshu.com/",
        "accept": "application/json, text/plain, */*",
    },
    "kuaishou": {
        "referer": "https://www.kuaishou.com/",
        "accept": "application/json, text/plain, */*",
    },
    "weibo": {
        "referer": "https://weibo.com/",
        "accept": "application/json, text/plain, */*",
    },
    "zhihu": {
        "referer": "https://www.zhihu.com/",
        "accept": "application/json, text/plain, */*",
    },
    "tieba": {
        "referer": "https://tieba.baidu.com/",
        "accept": "text/html,application/xhtml+xml",
    },
}


class RequestWrapper:
    """带平台风控与重试的统一请求封装"""

    def __init__(self, settings=None):
        settings = settings or {}
        self.rate_limiter = RateLimiter(
            min_interval=settings.get("default_min_interval", 3.0),
            max_rpm=settings.get("max_rpm", 20),
            ban_cooldown=settings.get("ban_cooldown", 300),
        )
        self.retry_policy = RetryPolicy(
            max_retries=settings.get("max_retries", 3),
            backoff=settings.get("retry_backoff", 5.0),
        )
        self.proxy_enabled = settings.get("proxy_enabled", False)
        self.session = requests.Session()
        self._cookies = {}  # platform -> cookie dict

    def _headers(self, platform, extra=None):
        headers = {
            "User-Agent": random.choice(UA_POOL),
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        headers.update(PLATFORM_HEADERS.get(platform, {}))
        if extra:
            headers.update(extra)
        return headers

    def _proxies(self):
        if not self.proxy_enabled:
            return None
        # 预留代理池接口（生产环境接入隧道代理）
        return None

    def set_cookies(self, platform, cookies: dict):
        self._cookies[platform] = cookies

    def get_cookie(self, platform, name, default=""):
        return self._cookies.get(platform, {}).get(name, default)

    @staticmethod
    def gen_csrf_token(platform):
        """生成平台风格 CSRF token（模拟）"""
        if platform == "zhihu":
            import base64
            import os

            return base64.b64encode(os.urandom(18)).decode()
        if platform == "tieba":
            return "BAIDUID=%032d" % random.randint(0, 10**32 - 1)
        return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=40))

    def get(self, platform, url, params=None, timeout=15):
        """带限速 + 重试的 GET 请求；返回 (status_code, text)"""
        self.rate_limiter.wait_if_needed(platform)
        headers = self._headers(platform)
        cookies = self._cookies.get(platform, {})
        attempt = 0
        while True:
            try:
                resp = self.session.get(
                    url, params=params, headers=headers, cookies=cookies,
                    proxies=self._proxies(), timeout=timeout,
                )
                if resp.status_code in (403, 418, 461):
                    # 平台风控特征码
                    cooldown = self.rate_limiter.mark_banned(platform, f"status={resp.status_code}")
                    return resp.status_code, ""
                if self.retry_policy.should_retry(attempt, status_code=resp.status_code):
                    attempt += 1
                    self.retry_policy.sleep_before_retry(attempt)
                    continue
                return resp.status_code, resp.text
            except requests.RequestException as exc:
                if self.retry_policy.should_retry(attempt, exception=exc):
                    attempt += 1
                    self.retry_policy.sleep_before_retry(attempt)
                    continue
                return -1, ""

    def post(self, platform, url, json=None, data=None, timeout=15):
        """带限速 + 重试的 POST 请求"""
        self.rate_limiter.wait_if_needed(platform)
        headers = self._headers(platform, {"content-type": "application/json"})
        cookies = self._cookies.get(platform, {})
        attempt = 0
        while True:
            try:
                resp = self.session.post(
                    url, json=json, data=data, headers=headers, cookies=cookies,
                    proxies=self._proxies(), timeout=timeout,
                )
                if resp.status_code in (403, 418, 461):
                    self.rate_limiter.mark_banned(platform, f"status={resp.status_code}")
                    return resp.status_code, ""
                if self.retry_policy.should_retry(attempt, status_code=resp.status_code):
                    attempt += 1
                    self.retry_policy.sleep_before_retry(attempt)
                    continue
                return resp.status_code, resp.text
            except requests.RequestException as exc:
                if self.retry_policy.should_retry(attempt, exception=exc):
                    attempt += 1
                    self.retry_policy.sleep_before_retry(attempt)
                    continue
                return -1, ""

    def parse_json(self, text):
        """安全解析 JSON"""
        if not text:
            return None
        import json

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None


def parse_html(text):
    """HTML 解析"""
    return BeautifulSoup(text, "lxml")
