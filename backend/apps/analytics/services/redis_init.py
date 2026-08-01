"""
Redis 缓存初始化配置
用于缓存热点数据，加速查询
"""
import logging
from typing import Optional

from apps.analytics.services.cache_manager import get_cache_manager, CacheManager

logger = logging.getLogger(__name__)

# 缓存过期时间常量（秒）
CACHE_TTL = {
    'DASHBOARD': 300,           # 数据大盘 5分钟
    'GEO_DATA': 600,            # 地理数据 10分钟
    'EXPLORER': 120,            # 探索数据 2分钟
    'KEYWORD_STATS': 600,       # 关键词统计 10分钟
    'PLATFORM_STATS': 600,      # 平台统计 10分钟
    'USER_PROFILE': 1800,       # 用户画像 30分钟
    'TREND_DATA': 900,          # 趋势数据 15分钟
    'HEATMAP': 600,             # 热力图 10分钟
    'ANALYSIS_RESULTS': 3600,   # 分析结果 1小时
    'RECOMMENDATIONS': 1800,    # 推荐数据 30分钟
}


def get_redis_cache() -> CacheManager:
    """获取 Redis 缓存管理器"""
    return get_cache_manager()


# 缓存键生成函数
def make_cache_key(*args, prefix: str = '') -> str:
    """生成统一的缓存键"""
    import hashlib
    raw = f"{prefix}:{':'.join(str(a) for a in args)}"
    return f"cc:{hashlib.md5(raw.encode()).hexdigest()[:16]}"


# 热点数据缓存装饰器
def cache_hot_data(expire: int = 300, prefix: str = 'hot'):
    """
    热点数据缓存装饰器
    
    用法：
        @cache_hot_data(expire=300, prefix='dashboard')
        def get_dashboard():
            ...
    """
    cache = get_redis_cache()
    return cache.cache(prefix, expire=expire)