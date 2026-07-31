# -*- coding: utf-8 -*-
"""行业词库 seed 命令

用法：
  python manage.py seed_industry_keywords                      # 打印词库统计
  python manage.py seed_industry_keywords --user admin --industry 装修家居   # 为指定用户导入某行业
  python manage.py seed_industry_keywords --user admin --all   # 为指定用户导入全部行业
  python manage.py seed_industry_keywords --export-json seed/industry_library.json  # 导出 JSON
"""
from django.core.management.base import BaseCommand

from apps.keywords.industry_library import (
    GLOBAL_NEGATIVE_WORDS,
    INDUSTRY_LIBRARY,
    all_negative_words,
    all_words,
    dump_json_file,
    industry_names,
)
from apps.keywords.models import Keyword, KeywordGroup


class Command(BaseCommand):
    help = "12 行业词库 seed：打印统计 / 导入指定用户关键词 / 导出 JSON"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, default="", help="目标用户名")
        parser.add_argument("--industry", type=str, default="", help="行业名（留空则打印统计）")
        parser.add_argument("--all", action="store_true", help="导入全部行业")
        parser.add_argument("--export-json", type=str, default="", help="导出 JSON 路径")

    def handle(self, *args, **options):
        export_json = options.get("export_json") or ""
        if export_json:
            path = dump_json_file(export_json)
            self.stdout.write(self.style.SUCCESS(f"词库已导出: {path}"))
            return

        # 打印统计
        total_main = sum(len(v["mainWords"]) for v in INDUSTRY_LIBRARY.values())
        total_long = sum(len(v["longTailWords"]) for v in INDUSTRY_LIBRARY.values())
        total_neg = sum(len(v["negativeWords"]) for v in INDUSTRY_LIBRARY.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"行业词库: {len(INDUSTRY_LIBRARY)} 行业 | "
                f"主词 {total_main} | 长尾词 {total_long} | 行业否定词 {total_neg} | "
                f"全局否定词 {len(GLOBAL_NEGATIVE_WORDS)}"
            )
        )
        for name in industry_names():
            self.stdout.write(f"  - {name}")

        username = options.get("user") or ""
        if not username:
            return

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if not user:
            self.stdout.write(self.style.ERROR(f"用户不存在: {username}"))
            return

        industries = []
        if options.get("all"):
            industries = industry_names()
        elif options.get("industry"):
            industries = [options["industry"]]

        total_created = 0
        for ind in industries:
            if ind not in INDUSTRY_LIBRARY:
                self.stdout.write(self.style.WARNING(f"未知行业: {ind}"))
                continue
            group, _ = KeywordGroup.objects.get_or_create(user=user, name=f"行业词库-{ind}")
            neg_words = ",".join(all_negative_words(ind))
            words = all_words(ind)
            created = 0
            for w in words:
                _, is_new = Keyword.objects.get_or_create(
                    user=user, word=w,
                    defaults={"group": group, "negative_words": neg_words, "hot_score": 80},
                )
                if is_new:
                    created += 1
            total_created += created
            self.stdout.write(
                self.style.SUCCESS(f"[{ind}] 导入 {created}/{len(words)} 个词（其余已存在）→ 分组「行业词库-{ind}」")
            )
        self.stdout.write(self.style.SUCCESS(f"全部完成，新增 {total_created} 个关键词"))
