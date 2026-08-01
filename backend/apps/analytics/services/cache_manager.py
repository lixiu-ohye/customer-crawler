"""
缓存管理器 - 基于 Redis 的缓存装饰器与数据缓存
Django 环境适配版
"""
import json
import hashlib
import logging
from typing import Any, Optional, Callable
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """统一的缓存管理器"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.StrictRedis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True,
                    socket_timeout=3,
                    socket_connect_timeout=3
                )
                self.redis_client.ping()
                self.redis_available = True
                logger.info('Redis 连接成功')
            except Exception as e:
                logger.warning(f'Redis 不可用，将使用内存缓存: {e}')
                self.redis_available = False
                self._memory_cache: dict[str, tuple] = {}
        else:
            logger.warning('redis 库未安装，将使用内存缓存')
            self.redis_available = False
            self._memory_cache: dict[str, tuple] = {}
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        raw = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"cc:{hashlib.md5(raw.encode()).hexdigest()[:16]}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self.redis_available:
            value = self.redis_client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            entry = self._memory_cache.get(key)
            if entry is None:
                return None
            value, expire_at = entry
            if expire_at and expire_at < __import__('time').time():
                del self._memory_cache[key]
                return None
            return value
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if self.redis_available:
                self.redis_client.setex(key, expire, serialized)
            else:
                import time
                expire_at = time.time() + expire if expire else None
                self._memory_cache[key] = (serialized, expire_at)
            return True
        except Exception as e:
            logger.error(f'缓存写入失败: {e}')
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self.redis_available:
                self.redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f'缓存删除失败: {e}')
            return False
    
    def clear(self, pattern: str = 'cc:*') -> bool:
        """清空缓存"""
        try:
            if self.redis_available:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                for key in list(self._memory_cache.keys()):
                    if key.startswith(pattern.replace('*', '')):
                        del self._memory_cache[key]
            return True
        except Exception as e:
            logger.error(f'清空缓存失败: {e}')
            return False
    
    def cache(self, prefix: str, expire: int = 3600, key_builder: Optional[Callable] = None):
        """
        缓存装饰器
        
        用法：
            @cache_manager.cache('dashboard', expire=300)
            def get_dashboard_data():
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self._make_key(prefix, *args, **kwargs)
                
                cached = self.get(cache_key)
                if cached is not None:
                    logger.debug(f'缓存命中: {cache_key}')
                    return cached
                
                result = func(*args, **kwargs)
                self.set(cache_key, result, expire)
                return result
            return wrapper
        return decorator


# 全局缓存管理器实例
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """获取缓存管理器"""
    return cache_manager
