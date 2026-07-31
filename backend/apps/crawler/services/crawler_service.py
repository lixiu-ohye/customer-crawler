"""六大平台爬虫：BaseCrawler 基类 + Douyin/Xiaohongshu/Kuaishou/Weibo/Zhihu/Tieba"""
import re
import time

from .request_wrapper import RequestWrapper

# 平台采集开关（实际部署时配置真实接口；当前实现为可运行的模拟适配层）
PLATFORM_ENABLED = {
    "douyin": False,
    "xiaohongshu": False,
    "kuaishou": False,
    "weibo": False,
    "zhihu": False,
    "tieba": False,
}


def extract_lng_lat(text):
    """从文本中提取经纬度 [lng, lat]，找不到返回 None"""
    if not text:
        return None
    m = re.search(r"(\d{2,3}\.\d{3,6})\s*[,，]\s*(\d{2}\.\d{3,6})", text)
    if m:
        return [float(m.group(1)), float(m.group(2))]
    return None


class BaseCrawler:
    """爬虫基类：定义采集协议"""

    platform = "base"

    def __init__(self, wrapper: RequestWrapper, config=None):
        self.wrapper = wrapper
        self.config = config or {}
        self.enabled = PLATFORM_ENABLED.get(self.platform, False)

    def search(self, keyword, page=1, page_size=20):
        """按关键词搜索，返回原始结果列表"""
        raise NotImplementedError

    def fetch_comments(self, item_id, page=1):
        """抓取评论"""
        raise NotImplementedError

    def normalize(self, raw):
        """原始数据 → 统一结构"""
        raise NotImplementedError


class DouyinCrawler(BaseCrawler):
    """抖音：搜索视频 + 评论"""

    platform = "douyin"
    SEARCH_URL = "https://www.douyin.com/aweme/v1/web/general/search/single/"
    COMMENT_URL = "https://www.douyin.com/aweme/v1/web/comment/list/"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        params = {
            "keyword": keyword,
            "search_channel": "aweme_general",
            "sort_type": 0,
            "publish_time": 0,
            "search_source": "normal_search",
            "query_correct_type": 1,
            "offset": (page - 1) * page_size,
            "count": page_size,
            "device_platform": "webapp",
            "aid": "6383",
        }
        status, text = self.wrapper.get(self.platform, self.SEARCH_URL, params=params)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        return (data.get("data") or {}).get("data") or []

    def fetch_comments(self, item_id, page=1):
        params = {"aweme_id": item_id, "cursor": (page - 1) * 20, "count": 20}
        status, text = self.wrapper.get(self.platform, self.COMMENT_URL, params=params)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        return (data.get("comments") or []) if isinstance(data, dict) else []

    def normalize(self, raw):
        desc = raw.get("aweme_info", {}).get("desc") or raw.get("desc") or ""
        author = ((raw.get("aweme_info") or {}).get("author") or {}).get("nickname") or ""
        stats = raw.get("aweme_info", {}).get("statistics") or {}
        return {
            "platform": "douyin",
            "item_id": str(raw.get("aweme_id") or raw.get("id") or ""),
            "title": desc[:100],
            "content": desc,
            "author": author,
            "author_id": str(((raw.get("aweme_info") or {}).get("author") or {}).get("uid") or ""),
            "url": f"https://www.douyin.com/video/{raw.get('aweme_id') or raw.get('id') or ''}",
            "like_count": stats.get("digg_count", 0),
            "comment_count": stats.get("comment_count", 0),
            "share_count": stats.get("share_count", 0),
            "publish_time": (raw.get("aweme_info") or {}).get("create_time"),
            "location": extract_lng_lat(desc),
            "extra": {},
        }


class XiaohongshuCrawler(BaseCrawler):
    """小红书：搜索笔记"""

    platform = "xiaohongshu"
    SEARCH_URL = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        params = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": "",
            "sort": "general",
            "note_type": 0,
        }
        status, text = self.wrapper.get(self.platform, self.SEARCH_URL, params=params)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        return ((data.get("data") or {}).get("items") or [])

    def normalize(self, raw):
        note = raw.get("note_card") or raw
        display = note.get("display_title") or note.get("title") or ""
        desc = note.get("desc") or display
        author = ((note.get("user") or {}).get("nickname")) or ""
        interactive = note.get("interact_info") or {}
        return {
            "platform": "xiaohongshu",
            "item_id": str(note.get("note_id") or ""),
            "title": display[:100],
            "content": desc,
            "author": author,
            "author_id": str(((note.get("user") or {}).get("user_id")) or ""),
            "url": f"https://www.xiaohongshu.com/explore/{note.get('note_id') or ''}",
            "like_count": interactive.get("liked_count", 0),
            "comment_count": interactive.get("comment_count", 0),
            "share_count": interactive.get("share_count", 0),
            "publish_time": note.get("time"),
            "location": extract_lng_lat(desc),
            "extra": {},
        }


class KuaishouCrawler(BaseCrawler):
    """快手：搜索作品"""

    platform = "kuaishou"
    SEARCH_URL = "https://www.kuaishou.com/graphql"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        payload = {
            "operationName": "graphqlSearch",
            "variables": {
                "keyword": keyword,
                "page": str(page),
                "pageSize": page_size,
                "pcursor": "",
            },
            "query": "",
        }
        status, text = self.wrapper.post(self.platform, self.SEARCH_URL, json=payload)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        return ((data.get("data") or {}).get("visionSearchPhoto") or {}).get("feeds") or []

    def normalize(self, raw):
        photo = raw.get("photo") or raw
        caption = photo.get("caption") or ""
        return {
            "platform": "kuaishou",
            "item_id": str(photo.get("id") or ""),
            "title": caption[:100],
            "content": caption,
            "author": (photo.get("user") or {}).get("name") or "",
            "author_id": str((photo.get("user") or {}).get("id") or ""),
            "url": photo.get("photoUrl") or f"https://www.kuaishou.com/short-video/{photo.get('id')}",
            "like_count": photo.get("realLikeCount", 0),
            "comment_count": photo.get("commentCount", 0),
            "share_count": photo.get("shareCount", 0),
            "publish_time": photo.get("timestamp"),
            "location": extract_lng_lat(caption),
            "extra": {},
        }


class WeiboCrawler(BaseCrawler):
    """微博：搜索微博"""

    platform = "weibo"
    SEARCH_URL = "https://m.weibo.cn/api/container/getIndex"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        params = {
            "containerid": "100103type=1&q=" + keyword,
            "page_type": "searchall",
            "page": page,
        }
        status, text = self.wrapper.get(self.platform, self.SEARCH_URL, params=params)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        cards = (data.get("data") or {}).get("cards") or []
        items = []
        for card in cards:
            card_group = card.get("card_group") or []
            items.extend(card_group)
        return items

    def normalize(self, raw):
        mblog = raw.get("mblog") or raw
        text = re.sub(r"<[^>]+>", "", mblog.get("text") or "")
        user = mblog.get("user") or {}
        return {
            "platform": "weibo",
            "item_id": str(mblog.get("id") or ""),
            "title": text[:100],
            "content": text,
            "author": user.get("screen_name") or "",
            "author_id": str(user.get("id") or ""),
            "url": f"https://weibo.com/{user.get('id') or ''}/{mblog.get('bid') or ''}",
            "like_count": (mblog.get("attitudes_count") or 0),
            "comment_count": (mblog.get("comments_count") or 0),
            "share_count": (mblog.get("reposts_count") or 0),
            "publish_time": mblog.get("created_at"),
            "location": extract_lng_lat(text),
            "extra": {},
        }


class ZhihuCrawler(BaseCrawler):
    """知乎：搜索问答"""

    platform = "zhihu"
    SEARCH_URL = "https://www.zhihu.com/api/v4/search_v3"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        params = {
            "t": "general",
            "q": keyword,
            "correction": 1,
            "offset": (page - 1) * page_size,
            "limit": page_size,
        }
        status, text = self.wrapper.get(self.platform, self.SEARCH_URL, params=params)
        data = self.wrapper.parse_json(text)
        if not data:
            return []
        return data.get("data") or []

    def normalize(self, raw):
        obj = raw.get("object") or raw
        content = obj.get("content") or ""
        excerpt = re.sub(r"<[^>]+>", "", content)[:500]
        author = ((obj.get("author") or {}).get("name")) or ""
        return {
            "platform": "zhihu",
            "item_id": str(obj.get("id") or ""),
            "title": (obj.get("title") or obj.get("question", {}).get("title") or excerpt[:100]),
            "content": excerpt,
            "author": author,
            "author_id": str((obj.get("author") or {}).get("id") or ""),
            "url": obj.get("url") or "",
            "like_count": obj.get("voteup_count", 0),
            "comment_count": obj.get("comment_count", 0),
            "share_count": 0,
            "publish_time": obj.get("created_time"),
            "location": extract_lng_lat(excerpt),
            "extra": {},
        }


class TiebaCrawler(BaseCrawler):
    """贴吧：搜索帖子（HTML 解析）"""

    platform = "tieba"
    SEARCH_URL = "https://tieba.baidu.com/f/search/res"

    def search(self, keyword, page=1, page_size=20):
        if not self.enabled:
            return []
        params = {"ie": "utf-8", "qw": keyword, "rn": page_size, "pn": (page - 1) * page_size}
        status, text = self.wrapper.get(self.platform, self.SEARCH_URL, params=params)
        from .request_wrapper import parse_html

        soup = parse_html(text)
        results = []
        for div in soup.select("div.s_post"):
            title_el = div.select_one("a.bluelink")
            author_el = div.select_one("span.p_author_name")
            content_el = div.select_one("span.post_content")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "author": author_el.get_text(strip=True) if author_el else "",
                    "content": content_el.get_text(strip=True) if content_el else "",
                })
        return results

    def normalize(self, raw):
        content = raw.get("content") or raw.get("title") or ""
        return {
            "platform": "tieba",
            "item_id": "",
            "title": raw.get("title", "")[:100],
            "content": content,
            "author": raw.get("author", ""),
            "author_id": "",
            "url": raw.get("url", ""),
            "like_count": 0,
            "comment_count": 0,
            "share_count": 0,
            "publish_time": raw.get("publish_time"),
            "location": extract_lng_lat(content),
            "extra": {},
        }


CRAWLER_CLASSES = {
    "douyin": DouyinCrawler,
    "xiaohongshu": XiaohongshuCrawler,
    "kuaishou": KuaishouCrawler,
    "weibo": WeiboCrawler,
    "zhihu": ZhihuCrawler,
    "tieba": TiebaCrawler,
}


class CrawlerService:
    """爬虫调度：多平台并行采集"""

    def __init__(self, settings=None):
        self.wrapper = RequestWrapper(settings)
        self.crawlers = {
            name: cls(self.wrapper, settings) for name, cls in CRAWLER_CLASSES.items()
        }

    def get_crawler(self, platform):
        return self.crawlers.get(platform)

    def crawl_keyword(self, platform, keyword, pages=1, progress_cb=None):
        """采集单平台单关键词；progress_cb(progress_dict) 汇报进度"""
        crawler = self.get_crawler(platform)
        if not crawler:
            return []
        all_items = []
        for page in range(1, pages + 1):
            raw_items = crawler.search(keyword, page=page)
            for raw in raw_items:
                try:
                    item = crawler.normalize(raw)
                    if item and item.get("content"):
                        all_items.append(item)
                except Exception:
                    continue
            if progress_cb:
                progress_cb({"page": page, "pages": pages, "found": len(all_items)})
            time.sleep(0.5)
        return all_items

    def crawl_multi(self, platforms, keyword, pages=1):
        """多平台采集，返回 {platform: [items]}"""
        results = {}
        for platform in platforms:
            crawler = self.get_crawler(platform)
            if not crawler:
                results[platform] = []
                continue
            if not crawler.enabled:
                results[platform] = []
                continue
            results[platform] = self.crawl_keyword(platform, keyword, pages=pages)
        return results
