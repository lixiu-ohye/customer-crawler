"""
分页工具类 - 支持 API 分页和懒加载
"""
from typing import List, Dict, Any, Optional
from math import ceil


class Pagination:
    """通用分页工具"""
    
    def __init__(self, page: int = 1, per_page: int = 20, total: int = 0):
        """
        初始化分页
        
        Args:
            page: 当前页码 (从 1 开始)
            per_page: 每页条数
            total: 总记录数
        """
        self.page = max(1, page)
        self.per_page = max(1, min(per_page, 100))  # 最多100条/页
        self.total = max(0, total)
        self.pages = ceil(self.total / self.per_page) if self.per_page > 0 else 0
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def prev_num(self) -> Optional[int]:
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self) -> Optional[int]:
        return self.page + 1 if self.has_next else None
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page
    
    def iter_pages(self, left_edge: int = 2, left_current: int = 2, 
                   right_current: int = 5, right_edge: int = 2) -> List[Optional[int]]:
        """
        生成分页页码迭代器
        
        Args:
            left_edge: 左边显示的页码数
            left_current: 当前页左边显示的页码数
            right_current: 当前页右边显示的页码数
            right_edge: 右边显示的页码数
            
        Yields:
            页码数字 或 None(表示省略号)
        """
        last = self.pages
        
        if last <= 1:
            return
        
        # 左边边缘
        left_end = left_edge + 1
        for num in range(1, min(left_end, last + 1)):
            yield num
        
        # 省略号
        if left_end < self.page - left_current:
            yield None
        
        # 当前页左边
        left_start = max(left_end, self.page - left_current)
        for num in range(left_start, self.page):
            if num > 0 and num <= last:
                yield num
        
        # 当前页
        yield self.page
        
        # 当前页右边
        right_end = min(last - right_edge, self.page + right_current)
        for num in range(self.page + 1, right_end + 1):
            if num <= last:
                yield num
        
        # 省略号
        if right_end < self.page + right_current:
            yield None
        
        # 右边边缘
        right_start = max(right_end + 1, last - right_edge + 1)
        for num in range(right_start, last + 1):
            yield num
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total': self.total,
            'pages': self.pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'prev_num': self.prev_num,
            'next_num': self.next_num
        }


class LazyLoader:
    """懒加载工具 - 支持游标分页"""
    
    def __init__(self, initial_cursor: int = 0, limit: int = 20):
        self.cursor = initial_cursor
        self.limit = max(1, min(limit, 50))  # 最多50条/次
    
    @property
    def has_more(self) -> bool:
        """判断是否还有更多数据（需要外部设置 total）"""
        return True  # 由外部判断
    
    def get_params(self) -> Dict[str, Any]:
        """获取查询参数"""
        return {
            'offset': self.cursor,
            'limit': self.limit
        }
    
    def update_cursor(self, last_id: int):
        """更新游标"""
        self.cursor = last_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cursor': self.cursor,
            'limit': self.limit
        }


def paginate_queryset(queryset, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """
    分页查询 Django QuerySet
    
    Args:
        queryset: Django QuerySet
        page: 页码
        per_page: 每页条数
        
    Returns:
        分页结果字典
    """
    total = queryset.count()
    pagination = Pagination(page, per_page, total)
    
    # 获取分页数据
    offset = pagination.offset
    items = list(queryset[offset:offset + pagination.per_page])
    
    return {
        'items': items,
        'pagination': pagination.to_dict()
    }


def lazy_load_items(items: List[Any], last_id: int, limit: int = 20) -> Dict[str, Any]:
    """
    懒加载数据
    
    Args:
        items: 数据列表
        last_id: 上次最后一条的ID
        limit: 本次加载条数
        
    Returns:
        懒加载结果
    """
    # 过滤出ID大于last_id的数据
    remaining = [item for item in items if getattr(item, 'id', 0) > last_id]
    
    # 返回指定数量
    loaded = remaining[:limit]
    has_more = len(remaining) > limit
    
    new_last_id = loaded[-1].id if loaded else last_id
    
    return {
        'items': loaded,
        'has_more': has_more,
        'last_id': new_last_id
    }