# -*- coding: utf-8 -*-
"""
抖音开放平台适配器
==================
官方接入: 抖音开放平台 (https://open.douyin.com)
- 文档: https://developer.open-douyin.com/docs/resource/zh-CN/dop/develop/openapi/video-search
- 凭证: client_key + client_secret (应用申请通过后获得)
- 搜索公开视频需申请「视频搜索」接口权限

合规说明:
- 仅调用官方开放接口, 只获取公开视频的标题/描述/作者昵称
- 不采集任何用户联系方式, 返回数据经基类统一脱敏
"""
import hashlib
import time
from typing import Any, Dict, List

import requests

from apps.crawler.official_apis.base import OfficialAPIAdapter, OfficialAPIError


class DouyinAdapter(OfficialAPIAdapter):
    PLATFORM = "douyin"
    PLATFORM_NAME = "抖音"
    CREDENTIAL_ENV = "DOUYIN_CLIENT_KEY"
    CREDENTIAL_KEY = "douyin"

    API_BASE = "https://open.douyin.com"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        client_key = self.credentials.get("client_key") or self.credentials.get("token")
        client_secret = self.credentials.get("client_secret", "")
        if not client_key:
            raise OfficialAPIError(self.PLATFORM, "缺少 client_key")

        access_token = self._get_access_token(client_key, client_secret)
        url = f"{self.API_BASE}/api/douyin/v1/video/search_video/"
        params = {
            "keyword": keyword,
            "count": min(limit, 10),
            "cursor": 0,
        }
        resp = requests.get(
            url,
            params=params,
            headers={"access-token": access_token, "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code != 200:
            raise OfficialAPIError(self.PLATFORM, f"搜索接口返回 {resp.status_code}", resp.status_code)
        data = resp.json()
        items = data.get("data", {}).get("videos", []) or []
        results = []
        for v in items:
            results.append({
                "id": v.get("video_id"),
                "title": v.get("title") or v.get("desc", ""),
                "content": v.get("desc", ""),
                "author": {"nickname": v.get("author", {}).get("nickname", "抖音用户"), "fans_count": v.get("author", {}).get("follower_count", 0)},
                "url": f"https://www.douyin.com/video/{v.get('video_id', '')}",
                "like_count": v.get("statistics", {}).get("digg_count", 0),
                "comment_count": v.get("statistics", {}).get("comment_count", 0),
                "share_count": v.get("statistics", {}).get("share_count", 0),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.get("create_time", time.time()))),
            })
        return results

    def _get_access_token(self, client_key: str, client_secret: str) -> str:
        """client_credentials 模式获取 access_token"""
        cache_key = f"douyin_token_{client_key}"
        cached = self._token_cache_get(cache_key)
        if cached:
            return cached
        resp = requests.post(
            f"{self.API_BASE}/oauth/access_token/",
            data={"client_key": client_key, "client_secret": client_secret, "grant_type": "client_credentials"},
            timeout=15,
        )
        if resp.status_code != 200:
            raise OfficialAPIError(self.PLATFORM, f"获取 token 失败: HTTP {resp.status_code}", resp.status_code)
        body = resp.json()
        token = body.get("data", {}).get("access_token")
        if not token:
            raise OfficialAPIError(self.PLATFORM, f"获取 token 失败: {body.get('data', {}).get('description', '未知错误')}")
        expires_in = int(body.get("data", {}).get("expires_in", 86400))
        self._token_cache_set(cache_key, token, expires_in - 60)
        return token

    _token_cache: Dict[str, tuple] = {}

    def _token_cache_get(self, key: str):
        entry = self._token_cache.get(key)
        if entry and entry[1] > time.time():
            return entry[0]
        return None

    def _token_cache_set(self, key: str, token: str, ttl: int):
        self._token_cache[key] = (token, time.time() + ttl)


class XiaohongshuAdapter(OfficialAPIAdapter):
    PLATFORM = "xiaohongshu"
    PLATFORM_NAME = "小红书"
    CREDENTIAL_ENV = "XHS_APP_ID"
    CREDENTIAL_KEY = "xiaohongshu"

    API_BASE = "https://edith.xiaohongshu.com/api"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        小红书目前没有面向个人开发者的公开搜索 API。
        官方通道:
          - 蒲公英平台 (品牌合作, 需企业资质): https://pgy.xiaohongshu.com
          - 专业号开放平台 (企业号): https://open.xiaohongshu.com
        未开放通用搜索接口时, 此适配器返回演示数据并标记 source=demo。
        若已获得企业级授权 (app_id + secret), 可在此实现笔记搜索接口。
        """
        app_id = self.credentials.get("app_id") or self.credentials.get("token")
        if not app_id:
            return self._demo_search(keyword, limit=limit, **kwargs)
        # 企业开放平台接入点 (示例, 以官方文档为准)
        # url = f"{self.API_BASE}/sns/v1/note/search"
        # resp = requests.get(url, params={...}, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        raise OfficialAPIError(
            self.PLATFORM,
            "小红书公开搜索接口未开放, 请接入专业号开放平台并实现对应接口 (预留实现点)",
        )


class KuaishouAdapter(OfficialAPIAdapter):
    PLATFORM = "kuaishou"
    PLATFORM_NAME = "快手"
    CREDENTIAL_ENV = "KUAISHOU_APP_KEY"
    CREDENTIAL_KEY = "kuaishou"

    API_BASE = "https://open.kuaishou.com"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        app_key = self.credentials.get("app_key") or self.credentials.get("token")
        if not app_key:
            return self._demo_search(keyword, limit=limit, **kwargs)
        # 快手开放平台: 视频搜索需企业认证 + 接口权限申请
        # url = f"{self.API_BASE}/rest/n/video/search"
        raise OfficialAPIError(
            self.PLATFORM,
            "快手开放平台视频搜索接口需企业认证, 请在开放平台申请对应权限后配置 (预留实现点)",
        )


class WeiboAdapter(OfficialAPIAdapter):
    PLATFORM = "weibo"
    PLATFORM_NAME = "微博"
    CREDENTIAL_ENV = "WEIBO_ACCESS_TOKEN"
    CREDENTIAL_KEY = "weibo"

    API_BASE = "https://api.weibo.com/2"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        access_token = self.credentials.get("access_token") or self.credentials.get("token")
        if not access_token:
            return self._demo_search(keyword, limit=limit, **kwargs)
        # 微博开放平台: 搜索接口 (需申请)
        # https://open.weibo.com/wiki/2/search/statuses
        resp = requests.get(
            f"{self.API_BASE}/search/statuses.json",
            params={"access_token": access_token, "q": keyword, "count": min(limit, 50)},
            timeout=15,
        )
        if resp.status_code != 200:
            raise OfficialAPIError(self.PLATFORM, f"搜索接口返回 {resp.status_code}", resp.status_code)
        data = resp.json()
        results = []
        for s in data.get("statuses", []):
            user = s.get("user", {})
            results.append({
                "id": s.get("idstr") or s.get("id"),
                "title": s.get("text", "")[:80],
                "content": s.get("text", ""),
                "author": {"nickname": user.get("screen_name", "微博用户"), "fans_count": user.get("followers_count", 0)},
                "url": f"https://weibo.com/{user.get('id', '')}/{s.get('mid', '')}",
                "like_count": s.get("attitudes_count", 0),
                "comment_count": s.get("comments_count", 0),
                "share_count": s.get("reposts_count", 0),
                "created_at": s.get("created_at", ""),
                "region": s.get("geo", {}).get("display_name", "未知") if isinstance(s.get("geo"), dict) else "未知",
            })
        return results


class ZhihuAdapter(OfficialAPIAdapter):
    PLATFORM = "zhihu"
    PLATFORM_NAME = "知乎"
    CREDENTIAL_ENV = "ZHIHU_TOKEN"
    CREDENTIAL_KEY = "zhihu"

    API_BASE = "https://api.zhihu.com"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        token = self.credentials.get("token")
        if not token:
            return self._demo_search(keyword, limit=limit, **kwargs)
        # 知乎开放平台 (zhihu open api) 暂未对个人开放通用搜索;
        # 此处为预留实现点: 接入知乎官方合作通道后实现
        raise OfficialAPIError(
            self.PLATFORM,
            "知乎开放平台未开放通用搜索接口, 请通过官方合作通道接入 (预留实现点)",
        )


class TiebaAdapter(OfficialAPIAdapter):
    PLATFORM = "tieba"
    PLATFORM_NAME = "贴吧"
    CREDENTIAL_ENV = "TIEBA_COOKIE"
    CREDENTIAL_KEY = "tieba"

    API_BASE = "https://tieba.baidu.com/f"

    def _search_impl(self, keyword: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        百度贴吧无官方开放 API。此适配器演示「合规公开数据」模式:
        - 仅在配置了合规数据源 (如授权合作方 / 公开 RSS) 时启用真实数据
        - 默认返回演示数据
        注意: 不得使用绕过风控手段抓取贴吧页面。
        """
        return self._demo_search(keyword, limit=limit, **kwargs)


# 注册全部适配器
from apps.crawler.official_apis.base import AdapterRegistry

AdapterRegistry.register(DouyinAdapter)
AdapterRegistry.register(XiaohongshuAdapter)
AdapterRegistry.register(KuaishouAdapter)
AdapterRegistry.register(WeiboAdapter)
AdapterRegistry.register(ZhihuAdapter)
AdapterRegistry.register(TiebaAdapter)
