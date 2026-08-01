# -*- coding: utf-8 -*-
"""行业导航与获客词库：12 行业导航 / 词库查询 / 推广员关注行业"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keywords.industry_library import INDUSTRY_LIBRARY, INDUSTRY_DESC
from apps.keywords.models import PromoterIndustry


# 演示线索数据（生产环境由 leads app 提供）
NAV_LEADS = [
    # 装修家居
    {"id": 1, "industry": "装修家居", "region": "深圳", "field": "全屋定制", "scenario": "新房装修", "need": "全屋定制报价方案", "contact": "张先生", "phone": "138****2211", "intent": 92},
    {"id": 2, "industry": "装修家居", "region": "广州", "field": "旧房翻新", "scenario": "老房改造", "need": "旧房翻新改造服务", "contact": "李女士", "phone": "139****8834", "intent": 85},
    {"id": 14, "industry": "装修家居", "region": "成都", "field": "防水补漏", "scenario": "卫生间漏水", "need": "卫生间漏水维修", "contact": "周先生", "phone": "158****3311", "intent": 88},
    {"id": 15, "industry": "装修家居", "region": "武汉", "field": "门窗定制", "scenario": "阳台封窗", "need": "阳台封窗报价", "contact": "吴女士", "phone": "157****8822", "intent": 76},
    # 本地生活家政服务
    {"id": 16, "industry": "本地生活家政服务", "region": "北京", "field": "家政保洁", "scenario": "深度保洁", "need": "新房深度保洁服务", "contact": "郑女士", "phone": "156****1100", "intent": 90},
    {"id": 17, "industry": "本地生活家政服务", "region": "上海", "field": "除甲醛", "scenario": "甲醛治理", "need": "新房除甲醛治理", "contact": "孙先生", "phone": "155****2211", "intent": 82},
    {"id": 18, "industry": "本地生活家政服务", "region": "杭州", "field": "家电清洗", "scenario": "空调清洗", "need": "空调深度清洗服务", "contact": "马女士", "phone": "154****3322", "intent": 71},
    # 汽车服务行业
    {"id": 19, "industry": "汽车服务行业", "region": "广州", "field": "二手车", "scenario": "二手车置换", "need": "二手车评估置换", "contact": "黄先生", "phone": "153****4433", "intent": 86},
    {"id": 20, "industry": "汽车服务行业", "region": "深圳", "field": "汽车贴膜", "scenario": "隐形车衣", "need": "隐形车衣施工报价", "contact": "林女士", "phone": "152****5544", "intent": 78},
    {"id": 21, "industry": "汽车服务行业", "region": "重庆", "field": "汽车维修", "scenario": "变速箱维修", "need": "变速箱维修报价", "contact": "罗先生", "phone": "151****6655", "intent": 69},
    # 美业医美
    {"id": 22, "industry": "美业医美", "region": "成都", "field": "轻医美", "scenario": "皮肤管理", "need": "光子嫩肤项目咨询", "contact": "唐女士", "phone": "150****7766", "intent": 91},
    {"id": 23, "industry": "美业医美", "region": "武汉", "field": "口腔种植", "scenario": "种植牙", "need": "种植牙价格咨询", "contact": "冯先生", "phone": "149****8877", "intent": 84},
    {"id": 24, "industry": "美业医美", "region": "长沙", "field": "美发造型", "scenario": "烫染护理", "need": "高端烫染套餐", "contact": "蒋女士", "phone": "148****9988", "intent": 63},
    # 教育培训
    {"id": 25, "industry": "教育培训", "region": "北京", "field": "K12辅导", "scenario": "中考冲刺", "need": "中考一对一辅导", "contact": "韩先生", "phone": "147****1109", "intent": 87},
    {"id": 26, "industry": "教育培训", "region": "西安", "field": "职业培训", "scenario": "技能考证", "need": "电工证培训报名", "contact": "杨女士", "phone": "146****2218", "intent": 79},
    {"id": 27, "industry": "教育培训", "region": "郑州", "field": "少儿编程", "scenario": "暑期班", "need": "少儿编程暑期班", "contact": "朱先生", "phone": "145****3327", "intent": 72},
    # 企业B端财税商务服务
    {"id": 28, "industry": "企业B端财税商务服务", "region": "上海", "field": "代理记账", "scenario": "公司注册", "need": "公司注册+代账套餐", "contact": "秦女士", "phone": "144****4436", "intent": 89},
    {"id": 29, "industry": "企业B端财税商务服务", "region": "深圳", "field": "税务筹划", "scenario": "汇算清缴", "need": "企业所得税汇算清缴", "contact": "尤先生", "phone": "143****5545", "intent": 83},
    {"id": 30, "industry": "企业B端财税商务服务", "region": "杭州", "field": "知识产权代理", "scenario": "商标注册", "need": "商标注册代理服务", "contact": "许女士", "phone": "142****6654", "intent": 77},
    # 房产同城服务
    {"id": 31, "industry": "房产同城服务", "region": "北京", "field": "二手房买卖", "scenario": "学区房", "need": "学区房购房咨询", "contact": "何先生", "phone": "141****7763", "intent": 93},
    {"id": 32, "industry": "房产同城服务", "region": "广州", "field": "房屋租赁", "scenario": "商铺出租", "need": "商铺租赁挂牌", "contact": "高女士", "phone": "140****8872", "intent": 74},
    {"id": 33, "industry": "房产同城服务", "region": "苏州", "field": "房产评估", "scenario": "抵押贷款评估", "need": "房产抵押评估报告", "contact": "郭先生", "phone": "139****9981", "intent": 68},
    # 婚庆摄影
    {"id": 34, "industry": "婚庆摄影", "region": "杭州", "field": "婚礼策划", "scenario": "中式婚礼", "need": "中式婚礼策划方案", "contact": "谢女士", "phone": "138****1107", "intent": 86},
    {"id": 35, "industry": "婚庆摄影", "region": "成都", "field": "婚纱摄影", "scenario": "旅拍", "need": "云南旅拍套餐", "contact": "谭先生", "phone": "137****2216", "intent": 81},
    {"id": 36, "industry": "婚庆摄影", "region": "重庆", "field": "跟拍服务", "scenario": "婚礼跟拍", "need": "婚礼全程跟拍", "contact": "罗女士", "phone": "136****3325", "intent": 66},
    # 口腔/健康理疗
    {"id": 37, "industry": "口腔/健康理疗", "region": "北京", "field": "牙齿矫正", "scenario": "隐形矫正", "need": "隐形牙套矫正咨询", "contact": "魏先生", "phone": "135****4434", "intent": 92},
    {"id": 38, "industry": "口腔/健康理疗", "region": "上海", "field": "中医理疗", "scenario": "颈椎调理", "need": "颈椎病中医理疗", "contact": "梁女士", "phone": "134****5543", "intent": 80},
    {"id": 39, "industry": "口腔/健康理疗", "region": "南京", "field": "健康体检", "scenario": "年度体检", "need": "企业年度体检套餐", "contact": "宋先生", "phone": "133****6652", "intent": 75},
    # 工程建材行业
    {"id": 40, "industry": "工程建材行业", "region": "武汉", "field": "防水材料", "scenario": "工程防水", "need": "工程防水材料供应", "contact": "谢先生", "phone": "132****7761", "intent": 85},
    {"id": 41, "industry": "工程建材行业", "region": "郑州", "field": "钢材供应", "scenario": "工地采购", "need": "螺纹钢批量采购", "contact": "彭先生", "phone": "131****8870", "intent": 79},
    {"id": 42, "industry": "工程建材行业", "region": "成都", "field": "涂料", "scenario": "外墙涂装", "need": "外墙涂料施工团队", "contact": "曾女士", "phone": "130****9989", "intent": 73},
    # 宠物行业
    {"id": 43, "industry": "宠物行业", "region": "深圳", "field": "宠物医疗", "scenario": "宠物绝育", "need": "宠物绝育手术咨询", "contact": "田女士", "phone": "129****1105", "intent": 88},
    {"id": 44, "industry": "宠物行业", "region": "上海", "field": "宠物寄养", "scenario": "节假日寄养", "need": "春节宠物寄养", "contact": "曹先生", "phone": "128****2214", "intent": 70},
    {"id": 45, "industry": "宠物行业", "region": "杭州", "field": "宠物美容", "scenario": "洗护造型", "need": "宠物美容年卡", "contact": "严女士", "phone": "127****3323", "intent": 64},
    # 互联网服务商
    {"id": 46, "industry": "互联网服务商（代运营/软件开发）", "region": "北京", "field": "代运营", "scenario": "电商代运营", "need": "天猫店铺代运营", "contact": "田先生", "phone": "126****4432", "intent": 90},
    {"id": 47, "industry": "互联网服务商（代运营/软件开发）", "region": "深圳", "field": "小程序开发", "scenario": "商城小程序", "need": "微信商城小程序开发", "contact": "华女士", "phone": "125****5541", "intent": 82},
    {"id": 48, "industry": "互联网服务商（代运营/软件开发）", "region": "广州", "field": "SEO优化", "scenario": "官网推广", "need": "企业官网SEO优化", "contact": "范先生", "phone": "124****6650", "intent": 71},
    # 法律行业（原有保留）
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
            leads = [x for x in leads if industry in x["industry"] or x["industry"] in industry]
        if region:
            leads = [x for x in leads if region in x["region"] or x["region"] in region]
        if field:
            leads = [x for x in leads if field in x["field"] or x["field"] in field]
        if scenario:
            leads = [x for x in leads if scenario in x["scenario"] or x["scenario"] in scenario]
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
