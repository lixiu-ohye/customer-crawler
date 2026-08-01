# -*- coding: utf-8 -*-
"""行业词库后台自动同步命令

由系统后台定时执行（Celery beat 每日 / cron），自动将 12 大行业词库
同步进关键词库，无需用户手动点击「一键导入」。

用法：
  python manage.py sync_industry_keywords                # 全量同步到所有非游客用户（默认 admin）
  python manage.py sync_industry_keywords --user admin   # 指定用户
  python manage.py sync_industry_keywords --dry-run      # 只打印统计，不写入
"""
from django.core.management.base import BaseCommand

from apps.keywords.models import Keyword, KeywordGroup
from apps.keywords.industry_library import INDUSTRY_LIBRARY, GLOBAL_NEGATIVE_WORDS
from apps.users.models import User


class Command(BaseCommand):
    help = '后台自动同步 12 大行业词库到关键词库（每日定时执行，用户无感）'

    def add_arguments(self, parser):
        parser.add_argument('--user', default='admin', help='目标用户名（默认 admin）')
        parser.add_argument('--dry-run', action='store_true', help='只统计不写入')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        username = options['user']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户不存在: {username}'))
            return

        total_created = 0
        total_skipped = 0
        industries = []
        for industry, lib in INDUSTRY_LIBRARY.items():
            words = list(lib.get('mainWords', [])) + list(lib.get('longTailWords', []))
            negatives = list(lib.get('negativeWords', [])) + list(GLOBAL_NEGATIVE_WORDS)
            group_name = f'行业词库-{industry}'
            group, _ = KeywordGroup.objects.get_or_create(
                user=user, name=group_name,
            )
            created = 0
            skipped = 0
            for w in words:
                kw, is_new = Keyword.objects.get_or_create(
                    user=user, word=w,
                    defaults={
                        'group': group,
                        'negative_words': ','.join(negatives),
                        'hot_score': 80,
                        'enabled': True,
                    },
                )
                if is_new:
                    created += 1
                    if not dry_run:
                        kw.group = group
                        kw.negative_words = ','.join(negatives)
                        kw.hot_score = 80
                        kw.enabled = True
                        kw.save(update_fields=['group', 'negative_words', 'hot_score', 'enabled'])
                else:
                    skipped += 1
            total_created += created
            total_skipped += skipped
            industries.append(f'{industry}(新{created}/跳{skipped})')

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY-RUN] 将同步 {len(industries)} 个行业: ' + ', '.join(industries)))
            self.stdout.write(self.style.WARNING(f'预计新增 {total_created} 词 / 跳过 {total_skipped} 词'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'后台自动同步完成: 用户 {username}，{len(industries)} 行业，新增 {total_created} 词 / 跳过 {total_skipped} 词'
            ))
            for line in industries:
                self.stdout.write('  ' + line)
