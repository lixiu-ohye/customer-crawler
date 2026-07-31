# -*- coding: utf-8 -*-
"""12 大行业词库（与行业痛点解决方案 pain-point-system 对齐）

每行业：mainWords 主词 + longTailWords 长尾词 + negativeWords 否定词
通用全局否定词：适用于所有行业
"""
import json

INDUSTRY_LIBRARY = {
    "装修家居": {
        "mainWords": ["装修", "旧房翻新", "防水补漏", "全屋定制", "门窗定制"],
        "longTailWords": [
            "家里装修大概多少钱", "老房子翻新方案", "卫生间漏水怎么修",
            "阳台封窗哪家好", "全屋定制报价", "新房装修流程",
            "厨房改造", "墙面渗水维修",
        ],
        "negativeWords": ["教程", "培训", "加盟", "招商", "厂家批发", "材料批发", "招聘", "设计图纸免费", "自媒体", "博主分享"],
    },
    "本地生活家政服务": {
        "mainWords": ["家政保洁", "开荒保洁", "除甲醛", "家电清洗", "搬家", "月嫂"],
        "longTailWords": [
            "新房开荒保洁价格", "甲醛治理有用吗", "空调清洗多少钱",
            "搬家公司推荐", "月嫂价格", "深度保洁",
            "下水道疏通", "保姆怎么找",
        ],
        "negativeWords": ["工具批发", "设备售卖", "培训课程", "加盟", "教学", "视频教程", "摆摊", "货源"],
    },
    "汽车服务行业": {
        "mainWords": ["二手车", "汽车维修", "汽车贴膜", "车险", "租车"],
        "longTailWords": [
            "本地二手私家车出售", "汽车保养价格", "车窗贴膜多少钱",
            "车险哪家划算", "短期租车", "事故车维修",
            "新能源维修",
        ],
        "negativeWords": ["车评", "测评", "博主", "批发配件", "汽配工厂", "教学", "改装教程", "赛事"],
    },
    "美业医美": {
        "mainWords": ["祛斑祛痘", "植发", "美甲美睫", "皮肤管理", "整形"],
        "longTailWords": [
            "脸上色斑怎么去除", "祛痘机构推荐", "植发大概费用",
            "纹眉价格", "产后瘦身", "双眼皮咨询",
        ],
        "negativeWords": ["教程", "自学", "工具批发", "培训学校", "加盟", "博主测评", "避坑视频", "货源"],
    },
    "教育培训": {
        "mainWords": ["早教", "公考培训", "学历提升", "技能培训", "托管班"],
        "longTailWords": [
            "成人自考怎么报名", "考公培训机构推荐", "幼儿托管收费",
            "会计培训班", "专升本途径",
        ],
        "negativeWords": ["资料免费下载", "网课资源", "题库", "教师招聘", "加盟办学", "课件分享"],
    },
    "企业B端财税商务服务": {
        "mainWords": ["注册公司", "代理记账", "商标注册", "资质办理"],
        "longTailWords": [
            "开公司流程", "小规模记账多少钱", "商标申请流程",
            "建筑资质办理", "公司注销手续",
        ],
        "negativeWords": ["教程自学", "模板下载", "招商加盟", "创业讲座", "课程培训", "电子书"],
    },
    "房产同城服务": {
        "mainWords": ["二手房", "租房", "新房", "商铺出租"],
        "longTailWords": [
            "本地两居室租房", "二手房首付多少", "商铺租金多少钱",
            "刚需新房推荐",
        ],
        "negativeWords": ["房产分析", "楼市预测", "投资讲座", "自媒体看房博主", "买房科普视频"],
    },
    "婚庆摄影": {
        "mainWords": ["婚纱摄影", "婚礼策划", "婚庆布置", "跟妆"],
        "longTailWords": [
            "婚纱照多少钱", "小型婚礼方案", "婚礼跟妆推荐",
            "生日派对布置",
        ],
        "negativeWords": ["道具批发", "教程自学", "素材模板", "摄影师接单平台", "教学课程"],
    },
    "口腔/健康理疗": {
        "mainWords": ["牙科", "牙齿矫正", "体检", "康复理疗", "中医推拿"],
        "longTailWords": [
            "隐形矫正价格", "洗牙多少钱", "牙周治疗",
            "中老年体检套餐", "腰间盘理疗",
        ],
        "negativeWords": ["医学科普", "论文", "自学", "药品批发", "养生视频博主"],
    },
    "工程建材行业": {
        "mainWords": ["建材", "工装施工", "厂房搭建", "工程机械租赁"],
        "longTailWords": [
            "办公室装修报价", "工地工程机械出租", "装修建材采购",
            "厂房改造施工",
        ],
        "negativeWords": ["工厂货源", "厂家直销", "招商", "展会资讯", "行业新闻", "批发价格表"],
    },
    "宠物行业": {
        "mainWords": ["宠物美容", "宠物医院", "宠物寄养", "猫狗售卖"],
        "longTailWords": [
            "猫咪疫苗价格", "狗狗寄养多少钱", "宠物皮肤病治疗",
            "纯种小猫多少钱",
        ],
        "negativeWords": ["饲养教程", "宠物测评", "用品批发", "进货渠道", "繁育教学"],
    },
    "互联网服务商（代运营/软件开发）": {
        "mainWords": ["小程序开发", "短视频代运营", "抖店运营", "网站搭建"],
        "longTailWords": [
            "商家小程序怎么做", "抖音店铺代运营费用", "企业官网搭建",
            "千川投放咨询",
        ],
        "negativeWords": ["免费源码", "自学教程", "素材下载", "课程培训", "教学直播", "模板免费领"],
    },
}

INDUSTRY_DESC = {
    "装修家居": "精准高转化行业",
    "本地生活家政服务": "需求量最大行业",
    "汽车服务行业": "汽车相关服务",
    "美业医美": "美容医疗行业",
    "教育培训": "教育培训行业",
    "企业B端财税商务服务": "B端高利润行业",
    "房产同城服务": "房产相关服务",
    "婚庆摄影": "婚庆摄影行业",
    "口腔/健康理疗": "医疗健康行业",
    "工程建材行业": "工程设备行业",
    "宠物行业": "宠物相关服务",
    "互联网服务商（代运营/软件开发）": "互联网电商行业",
}

GLOBAL_NEGATIVE_WORDS = [
    "攻略", "干货", "教程", "视频", "博主", "测评", "避坑",
    "加盟", "招商", "批发", "货源", "培训", "招聘", "图纸下载",
]


def get_industry(industry):
    """获取行业词库，返回 None 表示不存在"""
    return INDUSTRY_LIBRARY.get(industry)


def industry_names():
    """所有行业名"""
    return list(INDUSTRY_LIBRARY.keys())


def all_words(industry):
    """主词 + 长尾词"""
    lib = INDUSTRY_LIBRARY.get(industry)
    if not lib:
        return []
    return lib["mainWords"] + lib["longTailWords"]


def all_negative_words(industry):
    """行业否定词 + 全局否定词"""
    lib = INDUSTRY_LIBRARY.get(industry)
    neg = []
    if lib:
        neg = list(lib["negativeWords"])
    neg.extend(GLOBAL_NEGATIVE_WORDS)
    return list(dict.fromkeys(neg))  # 去重保序


def to_json():
    """导出完整词库 JSON（含全局否定词）"""
    return {
        "industries": industry_names(),
        "library": INDUSTRY_LIBRARY,
        "globalNegativeWords": GLOBAL_NEGATIVE_WORDS,
    }


def dump_json_file(path):
    """导出词库到 JSON 文件（seed 用）"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_json(), f, ensure_ascii=False, indent=2)
    return path
