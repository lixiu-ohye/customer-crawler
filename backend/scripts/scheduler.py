"""定时调度守护脚本：python scripts/scheduler.py
7×24 常驻：每分钟检查到期任务 + 每 6 小时执行 30 天数据清理
"""
import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

django.setup()

from django.conf import settings  # noqa: E402


def main():
    from apps.core.services import cleanup_expired_data
    from apps.tasks.services import task_service

    print(f"[scheduler] 启动，数据保留 {settings.COMPLIANCE['data_retention_days']} 天")
    last_cleanup = 0
    while True:
        try:
            # 1. 到期定时任务触发
            task_service.schedule_tasks()
            # 2. 每 6 小时清理过期数据
            now = time.time()
            if now - last_cleanup >= 6 * 3600:
                deleted = cleanup_expired_data()
                print(f"[scheduler] 数据清理完成，删除 {deleted} 条过期线索")
                last_cleanup = now
        except Exception as exc:
            print(f"[scheduler] 异常: {exc}")
        time.sleep(30)


if __name__ == "__main__":
    main()
