# -*- coding: utf-8 -*-
"""启动后台自动采集服务（独立进程，无人值守）
用法:
    python start_auto_crawl.py              # 全量 134 关键词循环
    python start_auto_crawl.py 3            # 只跑 3 个关键词（测试）
环境变量 AUTO_CRAWL_MAX_ITEMS 也可以限制。
"""
import os
import subprocess
import sys
from pathlib import Path

BACKEND = Path(r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\backend")
SCRIPT = BACKEND / "apps" / "crawler" / "services" / "auto_crawl.py"
LOG = BACKEND / "auto_crawl_out.log"

env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
if len(sys.argv) > 1:
    env["AUTO_CRAWL_MAX_ITEMS"] = sys.argv[1]

# 用 CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS 独立运行，不随 exec 会话退出
flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
with open(LOG, "w", encoding="utf-8") as logf:
    proc = subprocess.Popen(
        [sys.executable, "-u", str(SCRIPT)],
        stdout=logf,
        stderr=logf,
        creationflags=flags,
        cwd=str(BACKEND),
        env=env,
    )
print("auto_crawl started, PID:", proc.pid)
print("log:", LOG)
