# -*- coding: utf-8 -*-
"""行业导航与获客词库：12 行业导航 / 词库查询 / 推广员关注行业"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.industry_library import INDUSTRY_LIBRARY, INDUSTRY_DESC
from apps.keywords.models import PromoterIndustry


# 演示线索数据（生产环境由 leads app 提供）
NAV_LEADS = [
    {"id": 1, "industry": "装修家居", "region": "深圳", "field": "全屋定制", "scenario": "新房装修", "need": "全屋定制报价方案", "contact": "张先生", "phone": "138****2211", "intent": 92},
    {"id": 2, "industry": "装修家居", "region": "广州", "field": "旧房翻新", "scenario": "老房改造", "need": "旧房翻新改造服务", "contact": "李女士", "phone": "139****8834", "intent": 85},
    {"id": 3, "industry": "法律行业", "region": "北京", "field": "婚姻家庭", "scenario": "离婚财产分割", "need": "离婚财产分割法律咨询", "contact": "王先生", "phone": "136****5521", "intent": 95},
    {"id": 4, "industry": "法律行业", "region": "上海", "field": "交通事故", "scenario": "事故赔偿", "need": "交通事故赔偿标准咨询", "contact": "赵女士", "phone": "137****9987", "intent": 88},
    {"id": 5, "industry": "法律行业", "region": "深圳", "field": "劳动仲裁", "scenario": "欠薪维权", "need": "劳动仲裁申请代理", "contact": "陈先生", "phone": "135****4432", "intent": 90},
    {"id": 6, "industry": "法律行业", "region": "广州", "field": "刑事辩护", "scenario": "取保候审", "need": "刑事辩护律师委托", "contact": "刘女士", "phone": "134****2219", "intent": 97},
    {"id": 11, "industry": "法律行业", "region": "重庆", "field": "合同纠纷", "scenario": "货款拖欠", "need": "合同纠纷起诉代理", "contact": "钱先生", "phone": "159****6622", "intent": 93},
    {"id": 13, "industry": "法律行业", "region": "北京", "field": "知识产权", "scenario": "商标侵权", "need": "商标侵权维权诉讼", "contact": "何先生", "phone": "157****7789", "intent": 91},
]


class IndustryLeadsView(APIView):
    """行业地域导航 · 客户线索列表

    GET /keywords/industry-leads?industry=&region=&field=&scenario=&intent=
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """优先返回数据库中的真实爬虫线索；数据库为空时回退演示数据"""
        q = request.query_params
        industry = (q.get("industry") or "").strip()
        region = (q.get("region") or "").strip()
        field = (q.get("field") or "").strip()
        scenario = (q.get("scenario") or "").strip()
        intent_min = (q.get("intent") or "").strip()

        db_leads = self._db_leads(industry, region, field, scenario, intent_min)
        if db_leads:
            return Response({"results": db_leads, "total": len(db_leads), "source": "database"})

        # 回退：演示数据
        leads = NAV_LEADS
        if industry:
            leads = [x for x in leads if x["industry"] == industry]
        if region:
            leads = [x for x in leads if x["region"] == region]
        if field:
            leads = [x for x in leads if x["field"] == field]
        if scenario:
            leads = [x for x in leads if x["scenario"] == scenario]
        if intent_min:
            try:
                mi = int(intent_min)
                leads = [x for x in leads if x["intent"] >= mi]
            except ValueError:
                pass
        return Response({"results": leads, "total": len(leads), "source": "demo"})

    def _db_leads(self, industry="", region="", field="", scenario="", intent_min=""):
        """从 Lead 表读取爬虫采集的真实线索（仅意向非 none，按意向分倒序）"""
        from apps.leads.models import Lead
        qs = Lead.objects.exclude(intent_label="none").order_by("-intent_score", "-id")
        if industry:
            qs = qs.filter(tags__icontains=industry)
        if region:
            qs = qs.filter(region__icontains=region)
        if scenario:
            qs = qs.filter(title__icontains=scenario)
        if intent_min:
            try:
                qs = qs.filter(intent_score__gte=int(intent_min))
            except ValueError:
                pass
        rows = []
        for lead in qs[:100]:
            tags = lead.tags or []
            ind = tags[0] if tags else (lead.demand or "其他")
            rows.append({
                "id": lead.id,
                "industry": ind,
                "region": lead.region or "",
                "field": lead.demand or "",
                "scenario": lead.title or "",
                "need": lead.content or "",
                "contact": lead.author or "",
                "phone": "157****7789",
                "intent": lead.intent_score,
                "status": "待跟进" if lead.status == "new" else lead.status,
                "created_at": lead.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        return rows

class IndustryRegionsView(APIView):
    """地域热点（演示）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "results": {
                "hotspots": {
                    "北京": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "装修家居", "教育培训", "企业B端财税商务服务", "房产同城服务"],
                    "上海": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "装修家居", "教育培训", "企业B端财税商务服务"],
                    "广州": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "装修家居", "汽车服务行业", "美业医美"],
                    "深圳": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "装修家居", "互联网服务商（代运营/软件开发）", "企业B端财税商务服务"],
                    "江苏": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "工程建材行业", "宠物行业"],
                    "浙江": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "婚庆摄影", "教育培训"],
                    "广东": ["婚姻家庭", "刑事辩护", "交通事故", "劳动仲裁", "合同纠纷", "知识产权", "房产纠纷", "债权债务", "公司法务", "侵权赔偿", "汽车服务行业", "美业医美"],
                },
                "cities": ["北京", "上海", "广州", "深圳", "成都", "杭州", "南京", "武汉", "长沙", "重庆", "西安", "郑州", "岳阳", "周口"],
            }
        })


class IndustryTreeView(APIView):
    """行业→领域→场景→需求 drill-down（法律行业完整树，其他行业简化）"""

    permission_classes = [IsAuthenticated]

    LEGAL_TREE = {
        "婚姻家庭": {"fields": {"离婚纠纷": {"scenarios": {"离婚财产分割": ["离婚财产怎么分割", "离婚抚养权争取", "离婚房产归属"], "离婚抚养权": ["抚养权怎么判", "抚养费标准"]}, "needs": ["离婚财产分割法律咨询", "离婚协议起草", "抚养权诉讼代理"]}, "婚前协议": {"scenarios": {"婚前财产公证": ["婚前财产公证流程", "婚前协议怎么写"]}, "needs": ["婚前财产协议起草"]}}},
        "刑事辩护": {"fields": {"取保候审": {"scenarios": {"刑事拘留": ["刑事拘留多久", "取保候审条件"]}, "needs": ["取保候审申请", "刑事辩护律师委托"]}, "案件辩护": {"scenarios": {"开庭辩护": ["刑事案件开庭流程", "辩护律师怎么选"]}, "needs": ["刑事辩护代理", "会见嫌疑人"]}}},
        "交通事故": {"fields": {"事故赔偿": {"scenarios": {"事故责任认定": ["交通事故责任认定", "事故赔偿标准"]}, "needs": ["交通事故赔偿咨询", "事故诉讼代理"]}, "保险理赔": {"scenarios": {"保险理赔纠纷": ["保险理赔流程", "理赔金额争议"]}, "needs": ["保险理赔代理"]}}},
        "劳动仲裁": {"fields": {"欠薪维权": {"scenarios": {"工资拖欠": ["公司拖欠工资怎么办", "劳动仲裁申请流程"]}, "needs": ["劳动仲裁申请代理", "欠薪追讨法律咨询"]}, "工伤赔偿": {"scenarios": {"工伤认定": ["工伤认定标准", "工伤赔偿计算"]}, "needs": ["工伤赔偿代理"]}}},
        "合同纠纷": {"fields": {"货款拖欠": {"scenarios": {"合同违约": ["合同违约怎么起诉", "货款追讨"]}, "needs": ["合同纠纷起诉代理", "货款催收法律服务"]}, "合同审查": {"scenarios": {"合同风险": ["合同审查要点", "合同陷阱规避"]}, "needs": ["合同审查服务"]}}},
        "知识产权": {"fields": {"商标侵权": {"scenarios": {"商标被侵权": ["商标侵权怎么办", "商标维权流程"]}, "needs": ["商标侵权维权诉讼"]}, "专利保护": {"scenarios": {"专利申请": ["专利申请流程", "专利侵权判定"]}, "needs": ["专利代理申请"]}}},
        "房产纠纷": {"fields": {"二手房买卖": {"scenarios": {"买卖合同纠纷": ["二手房买卖纠纷处理", "房屋过户纠纷"]}, "needs": ["房产纠纷诉讼代理"]}, "租赁纠纷": {"scenarios": {"租房纠纷": ["租房合同纠纷", "押金退还纠纷"]}, "needs": ["房屋租赁纠纷咨询"]}}},
        "债权债务": {"fields": {"欠款催收": {"scenarios": {"民间借贷": ["欠钱不还怎么起诉", "借条法律效力"]}, "needs": ["债权催收代理", "民间借贷诉讼"]}, "债务重组": {"scenarios": {"企业债务": ["企业债务重组方案", "破产清算"]}, "needs": ["债务重组法律服务"]}}},
        "公司法务": {"fields": {"股权纠纷": {"scenarios": {"股权争议": ["股权纠纷怎么处理", "股东权益保护"]}, "needs": ["股权纠纷诉讼代理"]}, "企业合规": {"scenarios": {"公司治理": ["公司法律顾问服务", "企业合规审查"]}, "needs": ["企业常年法律顾问"]}}},
        "侵权赔偿": {"fields": {"人身损害": {"scenarios": {"人身伤害赔偿": ["人身损害赔偿标准", "伤残鉴定流程"]}, "needs": ["人身损害赔偿代理"]}, "名誉侵权": {"scenarios": {"名誉权纠纷": ["名誉侵权怎么起诉", "网络侵权维权"]}, "needs": ["名誉侵权诉讼代理"]}}},
    }

    def get(self, request):
        industry = (request.query_params.get("industry") or "").strip()
        if industry == "法律行业":
            return Response({"results": {"industry": industry, "tree": self.LEGAL_TREE}})
        from apps.keywords.industry_library import INDUSTRY_LIBRARY
        lib = INDUSTRY_LIBRARY.get(industry) or {}
        tree = {}
        for i, m in enumerate(lib.get("mainWords", [])):
            lt = lib.get("longTailWords", [])
            tree[m] = {
                "fields": {"常见需求": {
                    "scenarios": {m + "咨询": lt[i * 2:i * 2 + 2]},
                    "needs": [m + "服务咨询", m + "方案报价"],
                }}
            }
        return Response({"results": {"industry": industry, "tree": tree}})


class IndustryNavView(APIView):
    """行业导航：12 行业列表（含描述/预览词）+ 单行业词库

    GET /keywords/industry-nav              → { results: { industries: [{id,name,description,preview}], cities: [...] } }
    GET /keywords/industry-nav?industry=X   → { results: { industry, description, mainWords, longTailWords, negativeWords, globalNegativeWords, allNegativeWords } }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        industry = (request.query_params.get("industry") or "").strip()
        if industry:
            lib = INDUSTRY_LIBRARY.get(industry)
            if not lib:
                return Response({"detail": f"未知行业: {industry}"}, status=404)
            from apps.keywords.industry_library import (
                GLOBAL_NEGATIVE_WORDS,
                all_negative_words,
            )
            return Response({
                "results": {
                    "industry": industry,
                    "description": INDUSTRY_DESC.get(industry, ""),
                    "mainWords": lib["mainWords"],
                    "longTailWords": lib["longTailWords"],
                    "negativeWords": lib["negativeWords"],
                    "globalNegativeWords": GLOBAL_NEGATIVE_WORDS,
                    "allNegativeWords": all_negative_words(industry),
                }
            })
        industries = [
            {
                "id": i + 1,
                "name": name,
                "description": INDUSTRY_DESC.get(name, ""),
                "preview": INDUSTRY_LIBRARY[name]["mainWords"][:4],
            }
            for i, name in enumerate(INDUSTRY_LIBRARY.keys())
        ]
        return Response({"results": {
            "industries": industries,
            "cities": ["北京", "上海", "广州", "深圳", "成都", "杭州", "南京", "武汉", "长沙", "重庆", "西安", "郑州", "岳阳", "周口"],
        }})


class PromoterIndustryView(APIView):
    """推广员关注行业

    GET  /keywords/promoter-industries   → { results: { industries: [{id,name,description}] } }
    POST /keywords/promoter-industries   body: { industryIds: [1,2,3] } → 全量替换
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        follows = PromoterIndustry.objects.filter(user=request.user).select_related("user")
        industries = [
            {
                "id": f.industry_id,
                "name": f.industry_name,
                "description": INDUSTRY_DESC.get(f.industry_name, ""),
            }
            for f in follows
        ]
        return Response({"result": {"industries": industries}})

    def post(self, request):
        industry_ids = request.data.get("industryIds") or []
        name_by_id = {
            i + 1: name for i, name in enumerate(INDUSTRY_LIBRARY.keys())
        }
        # 全量替换
        PromoterIndustry.objects.filter(user=request.user).delete()
        created = 0
        for iid in industry_ids:
            try:
                iid = int(iid)
            except (TypeError, ValueError):
                continue
            name = name_by_id.get(iid)
            if not name:
                continue
            _, is_new = PromoterIndustry.objects.get_or_create(
                user=request.user, industry_id=iid,
                defaults={"industry_name": name},
            )
            if is_new:
                created += 1
        return Response({
            "result": {"saved": created, "industryIds": [int(x) for x in industry_ids]},
        })
