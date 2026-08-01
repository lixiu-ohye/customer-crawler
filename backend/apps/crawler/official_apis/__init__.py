# -*- coding: utf-8 -*-
"""
官方开放 API 合规采集层
========================
基于各平台官方开放平台 / 公开接口实现的合规数据采集适配器。

设计原则（合规红线）:
1. 只采集平台官方开放 API / 公开搜索接口允许返回的公开数据
2. 不采集手机号、微信号、私信、真实姓名等个人敏感信息
3. 不自动私信、不批量评论、不破解风控
4. 所有请求经过统一限速（rate_limiter）
5. 返回数据经过脱敏（data_anonymizer）
6. 数据默认 30 天自动清理（由 COMPLIANCE 配置控制）
7. 全程留痕（audit log）

接入方式:
- 用户申请各平台开放平台开发者权限后, 在环境变量 / .env 中配置对应
  API Key / Token, 即可从 "mock 演示模式" 切换为 "真实官方 API 模式"。
- 未配置凭证时自动降级为演示数据, 保证前端可运行。

支持平台: douyin(抖音) / xiaohongshu(小红书) / kuaishou(快手)
          weibo(微博) / zhihu(知乎) / tieba(贴吧)
"""
from apps.crawler.official_apis.base import OfficialAPIAdapter, OfficialAPIError, AdapterRegistry

__all__ = [
    "OfficialAPIAdapter",
    "OfficialAPIError",
    "AdapterRegistry",
]
