"""关键词视图"""
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.models import Keyword, KeywordGroup
from apps.keywords.services import KeywordService


def _serialize(kw):
    return {
        "id": kw.id,
        "word": kw.word,
        "group_id": kw.group_id,
        "group_name": kw.group.name if kw.group else "",
        "negative_words": kw.negative_words,
        "hot_score": kw.hot_score,
        "enabled": kw.enabled,
        "created_at": kw.created_at.strftime("%Y-%m-%d %H:%M:%S") if kw.created_at else "",
    }


class KeywordListView(APIView):
    """关键词列表 / 新增"""

    def get(self, request):
        qs = Keyword.objects.filter(user=request.user)
        group_id = request.query_params.get("group_id")
        search = request.query_params.get("search")
        if group_id:
            qs = qs.filter(group_id=group_id)
        if search:
            qs = qs.filter(word__icontains=search)
        data = [_serialize(k) for k in qs[:500]]
        return Response({"results": data, "total": qs.count()})

    def post(self, request):
        word = (request.data.get("word") or "").strip()
        if not word:
            return Response({"detail": "关键词不能为空"}, status=400)
        kw, created = Keyword.objects.get_or_create(
            user=request.user,
            word=word,
            defaults={
                "group_id": request.data.get("group_id"),
                "negative_words": request.data.get("negative_words", ""),
            },
        )
        return Response({"result": _serialize(kw), "created": created}, status=201 if created else 200)


class KeywordDetailView(APIView):
    """关键词详情 / 更新 / 删除"""

    def _get(self, request, pk):
        return Keyword.objects.filter(id=pk, user=request.user).first()

    def put(self, request, pk):
        kw = self._get(request, pk)
        if not kw:
            return Response({"detail": "不存在"}, status=404)
        if "negative_words" in request.data:
            kw.negative_words = request.data["negative_words"]
        if "enabled" in request.data:
            kw.enabled = bool(request.data["enabled"])
        if "group_id" in request.data:
            kw.group_id = request.data["group_id"] or None
        kw.save()
        return Response({"result": _serialize(kw)})

    def delete(self, request, pk):
        kw = self._get(request, pk)
        if not kw:
            return Response({"detail": "不存在"}, status=404)
        kw.delete()
        return Response({"detail": "已删除"})


class KeywordBulkView(APIView):
    """批量导入"""

    def post(self, request):
        words = request.data.get("words", [])
        if isinstance(words, str):
            words = [w for w in words.replace("\n", ",").split(",") if w.strip()]
        result = KeywordService.bulk_import(request.user, words)
        return Response(result)


class KeywordSuggestView(APIView):
    """自动联想"""

    def get(self, request):
        prefix = request.query_params.get("q", "")
        return Response({"results": KeywordService.suggest(request.user, prefix)})


class KeywordExpandView(APIView):
    """AI 拓词"""

    def post(self, request):
        seed = (request.data.get("seed") or "").strip()
        if not seed:
            return Response({"detail": "请提供种子词"}, status=400)
        result = KeywordService.ai_expand(
            request.user, seed,
            industry=request.data.get("industry"),
            city=request.data.get("city"),
        )
        return Response(result)


class KeywordGroupView(APIView):
    """分组管理"""

    def get(self, request):
        groups = KeywordGroup.objects.filter(user=request.user)
        return Response({
            "results": [
                {"id": g.id, "name": g.name, "count": g.keywords.count(),
                 "created_at": g.created_at.strftime("%Y-%m-%d") if g.created_at else ""}
                for g in groups
            ]
        })

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response({"detail": "分组名不能为空"}, status=400)
        group, created = KeywordGroup.objects.get_or_create(user=request.user, name=name)
        return Response({"id": group.id, "name": group.name}, status=201 if created else 200)
