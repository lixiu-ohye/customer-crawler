"""线索服务：筛选、分页、导出 csv/xlsx、收藏、备注、拉黑"""
import csv
import io

from django.db.models import Q

from apps.leads.models import Lead

# 行业→场景映射（与 importer 的 SCENE_INDUSTRY 反向）
INDUSTRY_SCENES = {
    "法律服务": ["法律咨询"],
    "装修家居": ["装修家居"],
    "本地生活家政服务": ["家政服务"],
    "教育培训": ["教育培训"],
    "美业医美": ["医美健康"],
    "汽车服务行业": ["汽车服务"],
    "企业B端财税商务服务": ["企业服务"],
    "本地生活": ["本地生活"],
    "电商零售": ["电商零售"],
    "金融理财": ["金融理财"],
}


def serialize_lead(lead):
    return {
        "id": lead.id,
        "task_id": lead.task_id,
        "platform": lead.platform,
        "item_id": lead.item_id,
        "title": lead.title,
        "content": lead.content[:200],
        "author": lead.author,
        "author_id": lead.author_id,
        "url": lead.url,
        "like_count": lead.like_count,
        "comment_count": lead.comment_count,
        "share_count": lead.share_count,
        "publish_time": lead.publish_time.strftime("%Y-%m-%d %H:%M:%S") if lead.publish_time else "",
        "region": lead.region,
        "demand": lead.demand,
        "intent_label": lead.intent_label,
        "intent_score": lead.intent_score,
        "tags": lead.tags,
        "lng": lead.lng,
        "lat": lead.lat,
        "location_text": lead.location_text,
        "status": lead.status,
        "note": lead.note,
        "is_favorite": lead.is_favorite,
        "is_blacklisted": lead.is_blacklisted,
        "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if lead.created_at else "",
    }


class LeadService:
    """线索业务逻辑"""

    @staticmethod
    def filter_queryset(user, params):
        qs = Lead.objects.filter(user=user)
        if params.get("platform"):
            qs = qs.filter(platform=params["platform"])
        if params.get("intent"):
            qs = qs.filter(intent_label=params["intent"])
        if params.get("region"):
            qs = qs.filter(region__icontains=params["region"])
        if params.get("demand"):
            qs = qs.filter(demand=params["demand"])
        if params.get("scene"):
            qs = qs.filter(demand=params["scene"])
        if params.get("industry"):
            # 行业 → 对应场景集合（tags 含行业名 或 demand 命中场景）
            scenes = INDUSTRY_SCENES.get(params["industry"], [])
            ind = params["industry"]
            qs = Lead.objects.filter(
                Q(demand__in=scenes) | Q(id__in=[l.id for l in qs if ind in (l.tags or [])])
            )
        if params.get("min_score") is not None:
            qs = qs.filter(intent_score__gte=int(params["min_score"]))
        if params.get("search"):
            qs = qs.filter(Q(title__icontains=params["search"]) | Q(content__icontains=params["search"]))
        if params.get("favorite") == "1":
            qs = qs.filter(is_favorite=True)
        if params.get("blacklisted") == "1":
            qs = qs.filter(is_blacklisted=True)
        else:
            qs = qs.filter(is_blacklisted=False)
        if params.get("task_id"):
            qs = qs.filter(task_id=params["task_id"])
        if params.get("real") == "1":
            # SQLite 不支持 JSON contains，用 Python 过滤
            ids = [l.id for l in qs if "真实数据" in (l.tags or [])]
            qs = Lead.objects.filter(id__in=ids)
        return qs

    @staticmethod
    def filter_options(user):
        """返回可用筛选项：行业 / 场景 / 地域 列表"""
        leads = Lead.objects.filter(user=user, is_blacklisted=False)
        industries = sorted({t for lead in leads for t in (lead.tags or [])
                             if t in INDUSTRY_SCENES})
        scenes = sorted({lead.demand for lead in leads if lead.demand})
        regions = sorted({lead.region for lead in leads if lead.region})
        return {"industries": industries, "scenes": scenes, "regions": regions}

    @staticmethod
    def export_csv(user, params):
        """导出 CSV（UTF-8 BOM，Excel 直接打开不乱码）"""
        qs = LeadService.filter_queryset(user, params)
        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["平台", "标题", "正文", "作者", "链接", "点赞", "评论", "转发",
                         "发布时间", "地域", "需求", "意向", "意向分", "备注"])
        for lead in qs[:5000]:
            writer.writerow([
                lead.get_platform_display(), lead.title, lead.content, lead.author, lead.url,
                lead.like_count, lead.comment_count, lead.share_count,
                lead.publish_time.strftime("%Y-%m-%d %H:%M") if lead.publish_time else "",
                lead.region, lead.demand, lead.get_intent_label_display(), lead.intent_score, lead.note,
            ])
        return output.getvalue().encode("utf-8")

    @staticmethod
    def export_xlsx(user, params):
        """导出 xlsx"""
        from openpyxl import Workbook
        from openpyxl.styles import Font

        qs = LeadService.filter_queryset(user, params)
        wb = Workbook()
        ws = wb.active
        ws.title = "客户线索"
        headers = ["平台", "标题", "正文", "作者", "链接", "点赞", "评论", "转发",
                   "发布时间", "地域", "需求", "意向", "意向分", "备注"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for lead in qs[:5000]:
            ws.append([
                lead.get_platform_display(), lead.title, lead.content, lead.author, lead.url,
                lead.like_count, lead.comment_count, lead.share_count,
                lead.publish_time.strftime("%Y-%m-%d %H:%M") if lead.publish_time else "",
                lead.region, lead.demand, lead.get_intent_label_display(), lead.intent_score, lead.note,
            ])
        return _xlsx_bytes(wb)

    @staticmethod
    def export_xlsx_legacy(user, params):
        return LeadService.export_xlsx(user, params)


def _xlsx_bytes(wb):
    import io as _io
    buf = _io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
