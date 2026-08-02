# -*- coding: utf-8 -*-
"""舆情监控模块视图 - 评论截流链路 API"""
import logging
from datetime import datetime
from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend as DFBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q, Max, Min
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.monitor.models import MonitorTarget, RawComment, IntentComment, TriggerRule, DmTemplate, AccountPool
from apps.monitor.services.comment_importer import import_comments, convert_to_lead
from apps.monitor.services.comment_crawler import start_comment_crawl, stop_comment_crawl, get_crawl_status

logger = logging.getLogger("monitor")


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MonitorTargetViewSet(viewsets.ModelViewSet):
    """监控目标管理"""
    queryset = MonitorTarget.objects.all()
    serializer_class = None  # 暂时不实现序列化器，直接返回字典
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'target_id']
    ordering_fields = ['created_at', 'last_pull_time', 'pull_interval_min']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取查询集，支持过滤"""
        queryset = super().get_queryset()
        
        # 状态过滤
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(monitor_status=status_filter)
        
        # 平台过滤
        platform_filter = self.request.query_params.get('platform')
        if platform_filter:
            queryset = queryset.filter(platform=platform_filter)
        
        # 目标类型过滤
        type_filter = self.request.query_params.get('target_type')
        if type_filter:
            queryset = queryset.filter(target_type=type_filter)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """获取监控目标列表，包含评论统计"""
        queryset = self.get_queryset()
        
        # 获取分页数据
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({"results": [], "total": 0})

        # 构建响应数据
        results = []
        for target in page:
            # 获取评论统计
            comment_stats = target.comments.aggregate(
                total_comments=Count('id'),
                latest_comment_time=Max('comment_time'),
                earliest_comment_time=Min('comment_time')
            )
            
            # 获取意图统计
            intent_stats = target.comments.aggregate(
                high_intent=Count('intent', filter=Q(intent__intent_score__gte=70)),
                medium_intent=Count('intent', filter=Q(intent__intent_score__gte=50) & Q(intent__intent_score__lt=70)),
                low_intent=Count('intent', filter=Q(intent__intent_score__lt=50))
            )
            
            results.append({
                "id": target.id,
                "target_type": target.target_type,
                "target_id": target.target_id,
                "platform": target.platform,
                "title": target.title,
                "monitor_status": target.monitor_status,
                "last_pull_time": target.last_pull_time.isoformat() if target.last_pull_time else None,
                "pull_interval_min": target.pull_interval_min,
                "created_at": target.created_at.isoformat(),
                "comment_stats": {
                    "total_comments": comment_stats['total_comments'] or 0,
                    "latest_comment_time": comment_stats['latest_comment_time'].isoformat() if comment_stats['latest_comment_time'] else None,
                    "earliest_comment_time": comment_stats['earliest_comment_time'].isoformat() if comment_stats['earliest_comment_time'] else None,
                },
                "intent_stats": {
                    "high_intent": intent_stats['high_intent'] or 0,
                    "medium_intent": intent_stats['medium_intent'] or 0,
                    "low_intent": intent_stats['low_intent'] or 0,
                }
            })

        return self.get_paginated_response({
            "results": results,
            "total": queryset.count()
        })

    def create(self, request, *args, **kwargs):
        """创建监控目标"""
        data = request.data
        
        # 验证必填字段
        required_fields = ['target_type', 'platform', 'target_id']
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Missing required field: {field}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 检查目标是否已存在
        existing = MonitorTarget.objects.filter(
            platform=data['platform'],
            target_type=data['target_type'],
            target_id=data['target_id']
        ).first()
        
        if existing:
            return Response(
                {"error": "Target already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建目标
        target = MonitorTarget.objects.create(
            target_type=data['target_type'],
            platform=data['platform'],
            target_id=data['target_id'],
            title=data.get('title', ''),
            pull_interval_min=data.get('pull_interval_min', 5),
            created_by=request.user
        )
        
        return Response({
            "id": target.id,
            "target_type": target.target_type,
            "target_id": target.target_id,
            "platform": target.platform,
            "title": target.title,
            "monitor_status": target.monitor_status,
            "pull_interval_min": target.pull_interval_min,
            "created_at": target.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """删除监控目标"""
        instance = self.get_object()
        
        # 停止正在运行的采集
        if instance.monitor_status == "active":
            stop_comment_crawl(instance)
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def start_crawl(self, request, *args, **kwargs):
        """启动评论采集"""
        target = self.get_object()
        result = start_comment_crawl(target)
        
        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def stop_crawl(self, request, *args, **kwargs):
        """停止评论采集"""
        target = self.get_object()
        result = stop_comment_crawl(target)
        
        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def crawl_status(self, request, *args, **kwargs):
        """获取采集状态"""
        target = self.get_object()
        status_info = get_crawl_status(target)
        return Response(status_info, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """评论管理（只读）"""
    queryset = RawComment.objects.select_related('target').prefetch_related('intent').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DFBackend]
    search_fields = ['content', 'nickname']
    ordering_fields = ['comment_time', 'pulled_at', 'intent_score']
    ordering = ['-comment_time']
    filterset_fields = ['platform', 'target', 'uid']

    def list(self, request, *args, **kwargs):
        """获取评论列表"""
        queryset = self.get_queryset()
        
        # 目标过滤
        target_id = request.query_params.get('target')
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        
        # 意图过滤
        intent_level = request.query_params.get('intent_level')
        if intent_level:
            queryset = queryset.filter(intent__level=intent_level)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({"results": [], "total": 0})

        # 构建响应数据
        results = []
        for comment in page:
            intent = comment.intent.first()
            results.append({
                "id": comment.id,
                "target_id": comment.target.id,
                "target_title": comment.target.title,
                "platform": comment.platform,
                "uid": comment.uid,
                "nickname": comment.nickname,
                "avatar_url": comment.avatar_url,
                "fan_cnt": comment.fan_cnt,
                "region": comment.region,
                "content": comment.content,
                "like_count": comment.like_count,
                "reply_count": comment.reply_count,
                "comment_time": comment.comment_time.isoformat() if comment.comment_time else None,
                "pulled_at": comment.pulled_at.isoformat(),
                "intent_score": intent.intent_score if intent else 0,
                "intent_level": intent.level if intent else None,
                "hit_keyword": intent.hit_keyword if intent else "",
                "is_converted": intent.is_converted if intent else False,
            })

        return self.get_paginated_response({
            "results": results,
            "total": queryset.count()
        })

    @action(detail=True, methods=['get'])
    def detail(self, request, *args, **kwargs):
        """获取评论详情"""
        comment = self.get_object()
        
        intent = comment.intent.first()
        
        response_data = {
            "id": comment.id,
            "target_id": comment.target.id,
            "target_title": comment.target.title,
            "platform": comment.platform,
            "uid": comment.uid,
            "nickname": comment.nickname,
            "avatar_url": comment.avatar_url,
            "fan_cnt": comment.fan_cnt,
            "region": comment.region,
            "content": comment.content,
            "like_count": comment.like_count,
            "reply_count": comment.reply_count,
            "parent_comment_id": comment.parent_comment_id,
            "comment_time": comment.comment_time.isoformat() if comment.comment_time else None,
            "pulled_at": comment.pulled_at.isoformat(),
            "intent_analysis": {
                "intent_score": intent.intent_score if intent else 0,
                "intent_level": intent.level if intent else None,
                "hit_keyword": intent.hit_keyword if intent else "",
                "is_ad": intent.is_ad if intent else False,
                "is_converted": intent.is_converted if intent else False,
                "llm_raw": intent.llm_raw if intent else {},
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def convert_to_lead(self, request, *args, **kwargs):
        """将评论用户转为线索"""
        comment = self.get_object()
        result = convert_to_lead(comment)
        
        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class TriggerRuleViewSet(viewsets.ModelViewSet):
    """触发规则管理"""
    queryset = TriggerRule.objects.all()
    serializer_class = None  # 暂时不实现序列化器，直接返回字典
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """获取触发规则列表"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({"results": [], "total": 0})

        results = []
        for rule in page:
            results.append({
                "id": rule.id,
                "name": rule.name,
                "cond_intent_min": float(rule.cond_intent_min),
                "cond_fan_min": rule.cond_fan_min,
                "cond_fan_max": rule.cond_fan_max,
                "cond_exclude_following": rule.cond_exclude_following,
                "action_type": rule.action_type,
                "template_id": rule.template.id if rule.template else None,
                "template_name": rule.template.name if rule.template else None,
                "round": rule.round,
                "enabled": rule.enabled,
                "created_at": rule.created_at.isoformat(),
            })

        return self.get_paginated_response({
            "results": results,
            "total": queryset.count()
        })

    def create(self, request, *args, **kwargs):
        """创建触发规则"""
        data = request.data
        
        # 创建规则
        rule = TriggerRule.objects.create(
            name=data['name'],
            cond_intent_min=data.get('cond_intent_min', 0.70),
            cond_fan_min=data.get('cond_fan_min', 50),
            cond_fan_max=data.get('cond_fan_max', 5000),
            cond_exclude_following=data.get('cond_exclude_following', True),
            action_type=data['action_type'],
            round=data.get('round', 1),
            enabled=data.get('enabled', True),
        )
        
        # 关联模板（如果提供了）
        if 'template_id' in data:
            try:
                template = DmTemplate.objects.get(id=data['template_id'])
                rule.template = template
                rule.save()
            except DmTemplate.DoesNotExist:
                pass
        
        return Response({
            "id": rule.id,
            "name": rule.name,
            "cond_intent_min": float(rule.cond_intent_min),
            "cond_fan_min": rule.cond_fan_min,
            "cond_fan_max": rule.cond_fan_max,
            "cond_exclude_following": rule.cond_exclude_following,
            "action_type": rule.action_type,
            "template_id": rule.template.id if rule.template else None,
            "template_name": rule.template.name if rule.template else None,
            "round": rule.round,
            "enabled": rule.enabled,
            "created_at": rule.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class DmTemplateViewSet(viewsets.ModelViewSet):
    """话术模板管理"""
    queryset = DmTemplate.objects.all()
    serializer_class = None  # 暂时不实现序列化器，直接返回字典
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """获取话术模板列表"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({"results": [], "total": 0})

        results = []
        for template in page:
            results.append({
                "id": template.id,
                "name": template.name,
                "round": template.round,
                "content": template.content,
                "media_type": template.media_type,
                "is_active": template.is_active,
                "created_at": template.created_at.isoformat(),
            })

        return self.get_paginated_response({
            "results": results,
            "total": queryset.count()
        })

    def create(self, request, *args, **kwargs):
        """创建话术模板"""
        data = request.data
        
        template = DmTemplate.objects.create(
            name=data['name'],
            round=data.get('round', 1),
            content=data['content'],
            media_type=data.get('media_type', 'text'),
            is_active=data.get('is_active', True),
        )
        
        return Response({
            "id": template.id,
            "name": template.name,
            "round": template.round,
            "content": template.content,
            "media_type": template.media_type,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class AccountPoolViewSet(viewsets.ReadOnlyModelViewSet):
    """账号池管理（只读）"""
    queryset = AccountPool.objects.all()
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DFBackend]
    search_fields = ['account_name']
    ordering_fields = ['health_score', 'updated_at']
    ordering = ['-health_score']
    filterset_fields = ['platform', 'status']

    def list(self, request, *args, **kwargs):
        """获取账号池列表"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is None:
            return Response({"results": [], "total": 0})

        results = []
        for account in page:
            results.append({
                "id": account.id,
                "platform": account.platform,
                "account_name": account.account_name,
                "status": account.status,
                "health_score": float(account.health_score),
                "today_sent": account.today_sent,
                "hourly_sent": account.hourly_sent,
                "last_sent_at": account.last_sent_at.isoformat() if account.last_sent_at else None,
                "last_error": account.last_error,
                "updated_at": account.updated_at.isoformat(),
            })

        return self.get_paginated_response({
            "results": results,
            "total": queryset.count()
        })