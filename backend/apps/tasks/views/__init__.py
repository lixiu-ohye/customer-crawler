"""任务视图：新建、状态筛选、进度、启动/暂停/终止/重试/删除"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.models import CrawlTask, serialize_task
from apps.tasks.services import task_service


class TaskListView(APIView):
    """任务列表 / 新建"""

    def get(self, request):
        qs = CrawlTask.objects.filter(user=request.user)
        status = request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        # 先同步队列最新状态
        for task in qs[:50]:
            task_service.sync_status(task)
        qs = CrawlTask.objects.filter(user=request.user)
        if status:
            qs = qs.filter(status=status)
        data = [serialize_task(t) for t in qs[:100]]
        return Response({"results": data, "total": qs.count()})

    def post(self, request):
        keywords = (request.data.get("keywords") or "").strip()
        platforms = request.data.get("platforms") or []
        if not keywords:
            return Response({"detail": "请填写关键词"}, status=400)
        if not platforms:
            return Response({"detail": "请选择平台"}, status=400)
        task = CrawlTask.objects.create(
            user=request.user,
            name=(request.data.get("name") or "").strip() or keywords[:20],
            keywords=keywords,
            platforms=platforms,
            pages=int(request.data.get("pages", 1) or 1),
            schedule_type=request.data.get("schedule_type", ""),
        )
        if task.schedule_type:
            from django.utils import timezone

            task.next_run_at = timezone.now()
            task.save()
            return Response({"result": serialize_task(task), "scheduled": True})
        task_service.start(task)
        task.refresh_from_db()
        return Response({"result": serialize_task(task)})


class TaskDetailView(APIView):
    """任务操作：启动 / 暂停 / 终止 / 重试 / 删除"""

    def _get(self, request, pk):
        return CrawlTask.objects.filter(id=pk, user=request.user).first()

    def get(self, request, pk):
        task = self._get(request, pk)
        if not task:
            return Response({"detail": "不存在"}, status=404)
        task_service.sync_status(task)
        task.refresh_from_db()
        return Response({"result": serialize_task(task)})

    def post(self, request, pk):
        """操作：start / pause / resume / stop / retry / delete"""
        task = self._get(request, pk)
        if not task:
            return Response({"detail": "不存在"}, status=404)
        action = request.data.get("action", "start")
        if action == "start":
            task_service.start(task)
        elif action == "pause":
            task_service.pause(task)
        elif action == "resume":
            task_service.resume(task)
        elif action == "stop":
            task_service.stop(task)
            task.refresh_from_db()
        elif action == "retry":
            task.status = "pending"
            task.message = ""
            task.finished_at = None
            task.save()
            task_service.start(task)
        elif action == "delete":
            task_service.stop(task)
            task.delete()
            return Response({"detail": "已删除"})
        else:
            return Response({"detail": "未知操作"}, status=400)
        task.refresh_from_db()
        return Response({"result": serialize_task(task)})
