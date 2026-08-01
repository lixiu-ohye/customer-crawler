# -*- coding: utf-8 -*-
"""
官方 API 适配器基类
==================
统一所有平台适配器的接口契约与公共能力:
- 凭证管理 (从 settings / 环境变量读取, 未配置时自动降级演示模式)
- 统一限速 (复用 services.rate_limiter.RateLimiter)
- 响应脱敏 (复用 services.data_cleaner / anonymizer)
- 结果规范化 (统一返回 dict 结构, 与前端 mock 数据结构兼容)
- 审计日志 (记录每次对外请求)
"""
import hashlib
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from django.conf import settings

logger = logging.getLogger("crawler.official_api")


class OfficialAPIError(Exception):
    """官方 API 调用异常"""

    def __init__(self, platform: str, message: str, status_code: Optional[int] = None):
        self.platform = platform
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{platform}] {message} (HTTP {status_code})" if status_code else f"[{platform}] {message}")


class OfficialAPIAdapter:
    """
    平台官方 API 适配器基类

    子类需实现:
      - PLATFORM      : 平台标识 (douyin / xiaohongshu / ...)
      - PLATFORM_NAME : 平台中文名
      - _search_impl(keyword, **kwargs) -> list[dict]  真实 API 搜索实现
    """

    PLATFORM = "base"
    PLATFORM_NAME = "基础平台"
    # 演示模式下返回的示例数据条数
    DEMO_RESULT_COUNT = 5
    # 凭证环境变量名 (子类覆盖)
    CREDENTIAL_ENV = ""
    # 凭证配置键 (settings.OFFICIAL_API_CREDENTIALS 中的键名)
    CREDENTIAL_KEY = ""

    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        self.credentials = credentials or self._load_credentials()
        self._rate_limiter = self._build_rate_limiter()

    # ---------- 凭证 ----------
    def _load_credentials(self) -> Dict[str, str]:
        """从 settings.OFFICIAL_API_CREDENTIALS 或环境变量加载凭证"""
        creds = getattr(settings, "OFFICIAL_API_CREDENTIALS", {}) or {}
        platform_creds = creds.get(self.PLATFORM, {}) or {}
        # 环境变量优先
        if self.CREDENTIAL_ENV:
            env_val = getattr(settings, "OFFICIAL_API_%s" % self.PLATFORM.upper(), None)
            if env_val:
                platform_creds["token"] = env_val
        return platform_creds

    @property
    def is_configured(self) -> bool:
        """是否配置了真实凭证 (未配置则走演示模式)"""
        return bool(self.credentials.get("token") or self.credentials.get("appkey") or self.credentials.get("api_key"))

    @property
    def mode(self) -> str:
        """当前生效模式: official_api(真实) / demo(演示)"""
        return "official_api" if self.is_configured else "demo"

    # ---------- 限速 ----------
    def _build_rate_limiter(self):
        from apps.crawler.services.rate_limiter import RateLimiter

        cfg = getattr(settings, "CRAWLER_SETTINGS", {}) or {}
        return RateLimiter(
            min_interval=float(cfg.get("default_min_interval", 3)),
            max_rpm=int(cfg.get("max_rpm", 20)),
            ban_cooldown=int(cfg.get("ban_cooldown", 300)),
        )

    def _wait(self):
        """按平台限速等待"""
        try:
            self._rate_limiter.wait_if_needed(self.PLATFORM)
        except Exception:
            time.sleep(1.0)

    # ---------- 脱敏 ----------
    def _anonymize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        数据脱敏: 移除 / 打码个人敏感字段。
        合规红线: 手机号、微信号、邮箱、真实姓名、详细地址一律不保留。
        """
        sensitive_keys = ("phone", "mobile", "wechat", "weixin", "email", "real_name", "id_card", "address")
        out = {}
        for k, v in item.items():
            kl = str(k).lower()
            if any(s in kl for s in sensitive_keys):
                continue  # 直接丢弃敏感字段
            if isinstance(v, str) and len(v) > 2000:
                v = v[:2000] + "…"  # 截断超长正文
            out[k] = v
        # 作者信息仅保留匿名昵称
        author = out.get("author") or {}
        if isinstance(author, dict):
            author = {
                "nickname": str(author.get("nickname", author.get("name", "匿名用户")))[:30],
                "gender": author.get("gender", "unknown"),
                "fans_count": author.get("fans_count", 0),
            }
            out["author"] = author
        elif isinstance(author, str):
            out["author"] = {"nickname": author[:30], "gender": "unknown", "fans_count": 0}
        return out

    # ---------- 结果规范化 ----------
    def normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """统一输出结构 (与前端 mock.js 的 LEADS 字段兼容)"""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        platform_name = self.PLATFORM_NAME
        return {
            "id": str(item.get("id") or uuid.uuid4().hex[:12]),
            "platform": self.PLATFORM,
            "platform_name": platform_name,
            "title": str(item.get("title") or item.get("content") or "")[:200],
            "content": str(item.get("content") or item.get("desc") or "")[:2000],
            "summary": str(item.get("summary") or "")[:300],
            "author": item.get("author") or {"nickname": "匿名用户", "gender": "unknown", "fans_count": 0},
            "url": str(item.get("url") or ""),
            "region": str(item.get("region") or "未知"),
            "like_count": int(item.get("like_count") or item.get("likes") or 0),
            "comment_count": int(item.get("comment_count") or item.get("comments") or 0),
            "share_count": int(item.get("share_count") or item.get("shares") or 0),
            "created_at": str(item.get("created_at") or item.get("publish_time") or now),
            "source": "official_api" if self.is_configured else "demo",
            "collected_at": now,
        }

    # ---------- 主入口 ----------
    def search(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        统一搜索入口

        Args:
            keyword: 关键词 (行业 / 产品 / 需求词)
            limit:   返回条数上限
        Returns:
            list[dict] 规范化后的线索数据
        """
        self._wait()
        try:
            if self.is_configured:
                raw = self._search_impl(keyword, limit=limit, **kwargs)
            else:
                raw = self._demo_search(keyword, limit=limit, **kwargs)
        except OfficialAPIError:
            raise
        except Exception as exc:  # 真实 API 失败时降级演示数据并记录
            logger.warning("[%s] official API failed, fallback to demo: %s", self.PLATFORM, exc)
            raw = self._demo_search(keyword, limit=limit, **kwargs)
        results = []
        for item in raw:
            safe = self._anonymize(item)
            results.append(self.normalize_item(safe))
        # 审计日志 (留痕)
        self._audit(keyword, len(results), self.mode)
        return results[:limit]

    # ---------- 演示数据 (未配置凭证时) ----------
    def _demo_search(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """生成带平台特征的演示线索数据"""
        now = int(time.time())
        seeds = [
            "正在找{0}解决方案，有推荐吗？",
            "想知道{0}哪家靠谱",
            "刚接触{0}，求入门建议",
            "{0}供应商怎么选？预算有限",
            "{0}行业有哪些坑？",
            "谁用过{0}，体验如何",
            "想了解{0}的最新玩法",
            "{0}案例分享",
            "{0}合作渠道有哪些",
        ]
        out = []
        import random

        random.seed(hash(keyword) % (2**32))
        for i in range(min(limit, self.DEMO_RESULT_COUNT)):
            tpl = seeds[i % len(seeds)]
            title = tpl.format(keyword)
            out.append({
                "id": f"{self.PLATFORM}_demo_{i}",
                "title": title,
                "content": f"用户分享关于「{keyword}」的真实经历与需求, 希望寻找靠谱服务商。",
                "author": {"nickname": f"用户_{random.randint(1000, 9999)}", "gender": "unknown", "fans_count": random.randint(0, 5000)},
                "url": f"https://demo.{self.PLATFORM}.com/post/{i}",
                "like_count": random.randint(0, 500),
                "comment_count": random.randint(0, 100),
                "share_count": random.randint(0, 50),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now - random.randint(0, 604800))),
                "region": random.choice(["广东", "浙江", "江苏", "北京", "上海", "四川"]),
            })
        return out

    # ---------- 子类实现 ----------
    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """真实官方 API 搜索实现 (子类覆盖)"""
        raise OfficialAPIError(self.PLATFORM, f"{self.PLATFORM_NAME} 官方 API 实现未配置")

    def fetch_detail(self, item_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """获取单条详情 (子类可覆盖)"""
        return None

    # ---------- 审计 ----------
    def _audit(self, keyword: str, count: int, mode: str):
        """审计留痕"""
        try:
            from apps.crawler.services.audit_log import audit_collection

            audit_collection(self.PLATFORM, keyword, count, mode)
        except Exception:
            logger.info("[audit] platform=%s keyword=%s count=%s mode=%s", self.PLATFORM, keyword, count, mode)


class AdapterRegistry:
    """平台适配器注册表"""

    _adapters: Dict[str, OfficialAPIAdapter] = {}

    @classmethod
    def register(cls, adapter_cls):
        cls._adapters[adapter_cls.PLATFORM] = adapter_cls()
        return adapter_cls

    @classmethod
    def get(cls, platform: str) -> Optional[OfficialAPIAdapter]:
        return cls._adapters.get(platform.lower())

    @classmethod
    def all(cls) -> Dict[str, OfficialAPIAdapter]:
        return cls._adapters

    @classmethod
    def platforms(cls) -> List[Dict[str, str]]:
        return [
            {"platform": a.PLATFORM, "name": a.PLATFORM_NAME, "mode": a.mode, "configured": a.is_configured}
            for a in cls._adapters.values()
        ]
