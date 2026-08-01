# -*- coding: utf-8 -*-
"""
MediaCrawler 集成视图
提供爬虫任务管理 API
"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crawler.integrations.mediacrawler_adapter import (
    MediaCrawlerAdapter,
    start_crawler,
    get_crawler_status,
    get_crawler_results
)


class MediaCrawlerTaskView(APIView):
    """MediaCrawler 任务管理"""
    
    # 支持的平台
    PLATFORMS = {
        "douyin": "抖音",
        "xiaohongshu": "小红书",
        "kuaishou": "快手",
        "weibo": "微博",
        "zhihu": "知乎",
        "tieba": "贴吧"
    }
    
    def get(self, request):
        """获取任务列表"""
        status = request.query_params.get("status")
        tasks = MediaCrawlerAdapter.list_tasks(status=status)
        return Response({"results": tasks})
    
    def post(self, request):
        """创建并启动爬虫任务"""
        platform = request.data.get("platform", "").lower()
        keyword = request.data.get("keyword", "")
        crawler_type = request.data.get("crawler_type", "search")
        
        # 验证参数
        if not keyword:
            return Response({"detail": "请提供关键词"}, status=400)
        
        if platform not in self.PLATFORMS:
            return Response({
                "detail": f"不支持的平台: {platform}",
                "supported_platforms": list(self.PLATFORMS.keys())
            }, status=400)
        
        # 启动爬虫
        result = start_crawler(platform, keyword, crawler_type)
        
        if result.get("success"):
            return Response(result)
        else:
            return Response(result, status=500)


class MediaCrawlerTaskDetailView(APIView):
    """单个任务详情"""
    
    def get(self, request, task_id):
        """获取任务状态"""
        result = get_crawler_status(task_id)
        
        if result.get("success"):
            return Response(result)
        else:
            return Response(result, status=404)
    
    def delete(self, request, task_id):
        """取消任务"""
        result = MediaCrawlerAdapter.cancel_task(task_id)
        
        if result.get("success"):
            return Response(result)
        else:
            return Response(result, status=400)


class MediaCrawlerTaskResultView(APIView):
    """获取任务结果"""
    
    def get(self, request, task_id):
        """获取爬取结果"""
        result = get_crawler_results(task_id)
        
        if result.get("success"):
            return Response(result)
        else:
            return Response(result, status=404)


class MediaCrawlerPlatformsView(APIView):
    """支持的平台列表"""
    
    PLATFORMS = {
        "douyin": {
            "name": "抖音",
            "code": "dy",
            "enabled": True,
            "description": "短视频平台"
        },
        "xiaohongshu": {
            "name": "小红书",
            "code": "xhs",
            "enabled": True,
            "description": "种草社区"
        },
        "kuaishou": {
            "name": "快手",
            "code": "ks",
            "enabled": True,
            "description": "短视频平台"
        },
        "weibo": {
            "name": "微博",
            "code": "wb",
            "enabled": True,
            "description": "社交媒体"
        },
        "zhihu": {
            "name": "知乎",
            "code": "zhihu",
            "enabled": True,
            "description": "问答社区"
        },
        "tieba": {
            "name": "贴吧",
            "code": "tieba",
            "enabled": True,
            "description": "兴趣社区"
        }
    }
    
    def get(self, request):
        """获取支持的平台列表"""
        return Response({"results": self.PLATFORMS})


class MediaCrawlerQuickStartView(APIView):
    """快速启动爬虫（简化接口）"""
    
    def post(self, request):
        """
        快速启动爬虫
        body: {"keyword": "宠物医院", "platforms": ["douyin", "xiaohongshu"]}
        """
        keyword = request.data.get("keyword", "")
        platforms = request.data.get("platforms", ["douyin"])
        
        if not keyword:
            return Response({"detail": "请提供关键词"}, status=400)
        
        results = []
        
        for platform in platforms:
            result = start_crawler(platform, keyword, "search")
            results.append({
                "platform": platform,
                **result
            })
        
        return Response({
            "keyword": keyword,
            "tasks": results
        })
