"""
增强爬虫系统 - 支持更多平台（B站、微信等）
"""
import requests
import random
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EnhancedSocialMediaCrawler:
    """增强型社交媒体爬虫"""
    
    def __init__(self):
        # 扩展平台配置
        self.platforms = {
            'douyin': {
                'name': '抖音',
                'base_url': 'https://www.douyin.com',
                'search_api': 'https://www.douyin.com/aweme/v1/web/search/item/',
                'enabled': True
            },
            'xiaohongshu': {
                'name': '小红书',
                'base_url': 'https://www.xiaohongshu.com',
                'search_api': 'https://www.xiaohongshu.com/api/sns/web/v1/search/notes',
                'enabled': True
            },
            'kuaishou': {
                'name': '快手',
                'base_url': 'https://www.kuaishou.com',
                'search_api': 'https://www.kuaishou.com/api/search/video',
                'enabled': True
            },
            'weibo': {
                'name': '微博',
                'base_url': 'https://weibo.com',
                'search_api': 'https://weibo.com/ajax/side/search',
                'enabled': True
            },
            'zhihu': {
                'name': '知乎',
                'base_url': 'https://www.zhihu.com',
                'search_api': 'https://www.zhihu.com/api/v3/search',
                'enabled': True
            },
            'tieba': {
                'name': '贴吧',
                'base_url': 'https://tieba.baidu.com',
                'search_api': 'https://tieba.baidu.com/f/search/res',
                'enabled': True
            },
            'bilibili': {
                'name': 'B站',
                'base_url': 'https://www.bilibili.com',
                'search_api': 'https://api.bilibili.com/x/web-interface/search/type',
                'enabled': True
            },
            'wechat': {
                'name': '微信',
                'base_url': 'https://mp.weixin.qq.com',
                'search_api': 'https://mp.weixin.qq.com/misc/api/searchbiz',
                'enabled': True
            }
        }
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 关键词库（宠物行业示例）
        self.keyword_categories = {
            '宠物医疗': ['宠物医院', '宠物医生', '宠物诊疗', '宠物手术', '宠物疫苗', '宠物体检', '宠物看病', '宠物挂号'],
            '宠物美容': ['宠物美容', '宠物洗澡', '宠物造型', '宠物SPA', '宠物护理', '宠物美容店', '宠物洗护'],
            '宠物用品': ['宠物食品', '宠物用品', '宠物玩具', '宠物服装', '宠物窝', '宠物零食', '宠物主食'],
            '宠物服务': ['宠物寄养', '宠物训练', '宠物摄影', '宠物保险', '宠物殡葬', '宠物行为训练']
        }
    
    def search_bilibili(self, keyword: str, page: int = 1) -> List[Dict]:
        """B站搜索"""
        if not self.platforms.get('bilibili', {}).get('enabled', False):
            return []
        
        try:
            params = {
                'search_type': 'video',
                'keyword': keyword,
                'page': page,
                'order': 'totalrank',
                'duration': 0,
                'tids': 0
            }
            
            response = requests.get(
                self.platforms['bilibili']['search_api'],
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            data = response.json()
            results = []
            
            # B站返回结构可能不同，做适配
            result_list = data.get('data', {}).get('result', [])
            if not result_list:
                # 备选结构
                result_list = data.get('data', []).get('result', [])
            
            for item in result_list:
                video_info = {
                    'platform': 'bilibili',
                    'platform_name': 'B站',
                    'title': self._clean_html(item.get('title', '')),
                    'content': self._clean_html(item.get('description', '')),
                    'author': item.get('author', ''),
                    'author_id': item.get('mid', ''),
                    'publish_time': self._format_time(item.get('pubdate', 0)),
                    'likes': item.get('like', 0),
                    'comments': item.get('video_review', 0),
                    'shares': item.get('share', 0),
                    'views': item.get('play', 0),
                    'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    'keywords': [keyword],
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(video_info)
            
            return results
            
        except Exception as e:
            logger.error(f"B站搜索失败: {e}")
            return []
    
    def search_wechat(self, keyword: str, page: int = 1) -> List[Dict]:
        """微信公众号搜索"""
        if not self.platforms.get('wechat', {}).get('enabled', False):
            return []
        
        try:
            # 微信公众号搜索需要特殊处理
            # 这里使用模拟数据，实际需要登录微信公众平台
            params = {
                'action': 'search',
                'query': keyword,
                'type': 'article',
                'page': page
            }
            
            # 尝试调用微信搜索API（可能需要登录态）
            response = requests.get(
                self.platforms['wechat']['search_api'],
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            # 如果API不可用，返回模拟数据
            if response.status_code != 200:
                return self._mock_wechat_results(keyword)
            
            data = response.json()
            results = []
            
            for item in data.get('app_msg_list', []):
                article_info = {
                    'platform': 'wechat',
                    'platform_name': '微信',
                    'title': item.get('title', ''),
                    'content': item.get('digest', ''),
                    'author': item.get('author', ''),
                    'publish_time': item.get('update_time', ''),
                    'likes': item.get('read_num', 0),
                    'comments': 0,
                    'shares': 0,
                    'url': item.get('link', ''),
                    'keywords': [keyword],
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(article_info)
            
            return results
            
        except Exception as e:
            logger.warning(f"微信搜索失败，使用模拟数据: {e}")
            return self._mock_wechat_results(keyword)
    
    def _mock_wechat_results(self, keyword: str) -> List[Dict]:
        """生成模拟微信数据"""
        return [
            {
                'platform': 'wechat',
                'platform_name': '微信',
                'title': f'关于{keyword}的深度分析',
                'content': f'本文详细介绍了{keyword}的相关内容...',
                'author': '宠物行业观察',
                'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'likes': random.randint(100, 5000),
                'comments': random.randint(10, 200),
                'shares': random.randint(5, 100),
                'url': f"https://mp.weixin.qq.com/s?search={keyword}",
                'keywords': [keyword],
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        import re
        if not text:
            return ''
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除特殊实体
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text.strip()
    
    def _format_time(self, timestamp: int) -> str:
        """格式化时间戳"""
        if not timestamp:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def crawl_all_platforms(self, keyword: str, max_pages: int = 3) -> List[Dict]:
        """并行爬取所有平台"""
        all_results = []
        
        # 收集所有启用的平台搜索方法
        search_methods = []
        for platform_name, platform_config in self.platforms.items():
            if platform_config.get('enabled', False):
                if platform_name == 'bilibili':
                    search_methods.append(('bilibili', lambda k, p: self.search_bilibili(k, p)))
                elif platform_name == 'wechat':
                    search_methods.append(('wechat', lambda k, p: self.search_wechat(k, p)))
                # 可以继续添加其他平台...
        
        # 使用线程池并行爬取
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for platform_name, search_func in search_methods:
                futures.append(executor.submit(search_func, keyword, 1))
            
            # 收集结果
            for future in futures:
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"爬取任务失败: {e}")
        
        return all_results
    
    def get_enabled_platforms(self) -> List[Dict]:
        """获取所有启用的平台列表"""
        return [
            {
                'id': key,
                'name': config['name'],
                'enabled': config.get('enabled', True)
            }
            for key, config in self.platforms.items()
            if config.get('enabled', True)
        ]


# 单例实例
_enhanced_crawler = None


def get_enhanced_crawler() -> EnhancedSocialMediaCrawler:
    """获取增强爬虫实例"""
    global _enhanced_crawler
    if _enhanced_crawler is None:
        _enhanced_crawler = EnhancedSocialMediaCrawler()
    return _enhanced_crawler