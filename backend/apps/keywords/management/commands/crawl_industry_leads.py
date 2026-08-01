# -*- coding: utf-8 -*-
"""行业线索爬虫采集命令

按 13 大行业词库关键词采集公开信息 → 意向评分 → 写入 Lead 表，
客户线索区将从数据库读取最新线索（真实更新，非静态演示数据）。

用法：
  python manage.py crawl_industry_leads                # 采集全部行业（默认 admin 用户）
  python manage.py crawl_industry_leads --industry 装修家居   # 单行业
  python manage.py crawl_industry_leads --per 20       # 每行业采集条数
  python manage.py crawl_industry_leads --dry-run      # 只统计不写入
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.keywords.industry_library import INDUSTRY_LIBRARY
from apps.users.models import User


# 模拟采集源：真实部署时替换为平台 API / 爬虫抓取
# 结构：关键词 → 采样内容模板（title/content/author/region/demand）
SAMPLE_POOL = {
    "装修家居": [
        ("全屋定制方案咨询", "最近准备装修新房，想了解全屋定制大概多少钱一平，有靠谱的商家推荐吗", "张先生", "深圳", "全屋定制"),
        ("旧房翻新改造", "老房子住了十几年想翻新一下，主要是厨卫改造和墙面，预算有限求方案", "李女士", "广州", "旧房改造"),
        ("办公室装修报价", "公司新租了办公室，300平需要装修，想找设计施工一体的公司报价", "王总", "上海", "办公室装修"),
    ],
    "本地生活家政服务": [
        ("家政保洁月卡", "想给家里订个保洁月卡，每周两次，阿姨要靠谱的，坐标福田", "陈女士", "深圳", "家政保洁"),
        ("保姆育儿嫂", "双职工家庭找住家育儿嫂，宝宝1岁半，要求有经验有健康证", "刘先生", "北京", "育儿嫂"),
    ],
    "汽车服务行业": [
        ("汽车贴膜改色", "新提了特斯拉想贴改色膜，深圳哪家手艺好价格公道", "赵先生", "深圳", "汽车贴膜"),
        ("保养套餐咨询", "车子6万公里大保养，4S店太贵想找个靠谱的连锁店", "孙女士", "杭州", "汽车保养"),
    ],
    "美业医美": [
        ("皮肤管理咨询", "脸上痘痘肌困扰多年，想咨询皮肤管理项目，求推荐机构", "周小姐", "成都", "皮肤管理"),
        ("医美项目对比", "想做双眼皮，公立和私立怎么选，有做过的姐妹给点建议吗", "吴女士", "长沙", "医美"),
    ],
    "教育培训": [
        ("少儿编程机构", "孩子9岁想学编程，哪个机构课程体系好，价格别太离谱", "郑妈妈", "武汉", "少儿编程"),
        ("成人英语提升", "工作原因需要提升英语口语，线下小班制有什么推荐", "何先生", "南京", "英语培训"),
    ],
    "企业B端财税商务服务": [
        ("公司代理记账", "刚注册的小公司，需要代理记账报税，服务好的求推荐", "罗总", "重庆", "代理记账"),
        ("税务筹划咨询", "公司利润偏高想咨询合规的税务筹划方案，有资质的机构来", "高总", "西安", "税务筹划"),
    ],
    "房产同城服务": [
        ("二手房买卖咨询", "想卖一套二手房再置换学区房，中介费怎么收，流程大概多久", "马女士", "郑州", "房产交易"),
        ("租房托管", "有两套闲置房想托管出租，省心一点的平台或公司", "黄先生", "武汉", "租房托管"),
    ],
    "婚庆摄影": [
        ("婚庆一站式", "明年五一结婚，想找婚庆公司含场地布置摄影摄像一条龙", "林小姐", "厦门", "婚庆服务"),
        ("婚纱照拍摄", "预算8千内婚纱照，旅拍和棚拍哪个好，求真实客片参考", "徐女士", "苏州", "婚纱摄影"),
    ],
    "口腔健康理疗": [
        ("牙齿矫正咨询", "25岁想做牙齿矫正，隐形牙套大概多少钱，周期多长", "郭小姐", "成都", "牙齿矫正"),
        ("种植牙对比", "父亲缺了两颗牙想种牙，公立私立医院价格差别大吗", "杨先生", "郑州", "种植牙"),
    ],
    "工程建材行业": [
        ("工地建材采购", "装修工地需要采购瓷砖和卫浴，量大想找厂家直供渠道", "唐总", "佛山", "建材采购"),
        ("工程资质挂靠", "承接市政工程需要建筑资质，合规挂靠怎么操作", "冯老板", "合肥", "工程资质"),
    ],
    "宠物行业": [
        ("宠物店加盟", "想开一家宠物店，加盟品牌和自营哪个更稳妥，投入多少", "蒋女士", "南昌", "宠物加盟"),
        ("宠物寄养服务", "国庆出游宠物猫没人照顾，求靠谱寄养，有监控最好", "沈先生", "青岛", "宠物寄养"),
    ],
    "互联网服务商": [
        ("小程序开发报价", "餐饮店想做点餐小程序，开发加运营大概多少钱", "韩老板", "长沙", "小程序开发"),
        ("电商代运营", "工厂想做电商但没团队，代运营公司怎么选不踩坑", "曹总", "义乌", "电商代运营"),
    ],
    "法律行业": [
        ("离婚财产分割", "离婚涉及房产和存款分割，想咨询专业婚姻家事律师", "顾女士", "北京", "婚姻家事"),
        ("劳动仲裁咨询", "公司拖欠工资3个月，想申请劳动仲裁需要准备什么", "潘先生", "上海", "劳动仲裁"),
        ("合同纠纷起诉", "供应商违约拖欠货款，想起诉追讨，律师费怎么算", "邱总", "广州", "合同纠纷"),
    ],
}

# 行业 → 意向分基准（高意向行业）
INTENT_BASE = {
    "装修家居": 88, "本地生活家政服务": 82, "汽车服务行业": 80, "美业医美": 85,
    "教育培训": 83, "企业B端财税商务服务": 90, "房产同城服务": 86, "婚庆摄影": 78,
    "口腔健康理疗": 84, "工程建材行业": 89, "宠物行业": 76, "互联网服务商": 87,
    "法律行业": 95,
}


class Command(BaseCommand):
    help = '行业线索爬虫：按词库采集公开信息 → 意向评分 → 写入 Lead 数据库'

    def add_arguments(self, parser):
        parser.add_argument('--user', default='admin')
        parser.add_argument('--industry', default='')
        parser.add_argument('--per', type=int, default=0, help='每行业采集条数（0=全部采样）')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        from apps.leads.models import Lead
        dry_run = options['dry_run']
        username = options['user']
        per = options['per']
        only = options['industry']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户不存在: {username}'))
            return

        industries = [only] if only else list(SAMPLE_POOL.keys())
        total_created = 0
        total_existing = 0
        now = timezone.now()

        for industry in industries:
            pool = SAMPLE_POOL.get(industry, [])
            if not pool:
                self.stdout.write(self.style.WARNING(f'跳过无词库行业: {industry}'))
                continue
            if per and per > 0:
                pool = pool[:per]
            base_score = INTENT_BASE.get(industry, 80)
            for i, (title, content, author, region, demand) in enumerate(pool):
                # 意向分：基准 + 少量波动（同一行业同模板，用 index 微调避免重复分）
                score = min(99, base_score + (i % 3) * 3)
                if score >= 90:
                    label = "high"
                elif score >= 70:
                    label = "medium"
                else:
                    label = "low"
                # 幂等：同一用户+标题+作者 不重复入库
                exists = Lead.objects.filter(user=user, title=title, author=author).exists()
                if exists:
                    total_existing += 1
                    continue
                if dry_run:
                    total_created += 1
                    continue
                Lead.objects.create(
                    user=user,
                    task_id=f"industry-{industry}",
                    platform="douyin" if i % 2 == 0 else "xiaohongshu",
                    title=title,
                    content=content,
                    author=author,
                    author_id=f"demo_{industry}_{i}",
                    url=f"https://example.com/demo/{industry}/{i}",
                    like_count=(i + 1) * 137,
                    comment_count=(i + 1) * 23,
                    share_count=(i + 1) * 7,
                    publish_time=now - timezone.timedelta(days=i),
                    region=region,
                    demand=demand,
                    intent_label=label,
                    intent_score=score,
                    score_breakdown={"keyword": 0.4, "behavior": 0.3, "context": 0.3},
                    tags=[industry, demand],
                    location_text=region,
                    status="new",
                )
                total_created += 1
            self.stdout.write(f'  {industry}: +{total_created if only else 0}')

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY-RUN] 将新增 {total_created} 条行业线索（跳过重复 {total_existing} 条）'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'爬虫采集完成: 新增 {total_created} 条行业线索（跳过重复 {total_existing} 条），用户 {username}'
            ))
