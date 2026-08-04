# -*- coding: utf-8 -*-
"""最终精简：content 80字符 + title 40 + 去冗余字段，目标 <4.5MB"""
import json, os, datetime

SRC = r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\frontend\src\api\real-data.json"
DST = r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\frontend\public\real-data.json"

with open(SRC, "r", encoding="utf-8") as f:
    d = json.load(f)

leads = d.get("leads", [])
for l in leads:
    if l.get("content") and len(l["content"]) > 80:
        l["content"] = l["content"][:80]
    if l.get("title") and len(l["title"]) > 40:
        l["title"] = l["title"][:40]
    for k in ("score_breakdown", "note", "location_text", "item_id", "author_id", "url", "is_favorite", "is_blacklisted", "status", "demand"):
        l.pop(k, None)

d["leads"] = leads
d["trimmed_content"] = True
d["trimmed_at"] = datetime.datetime.now().isoformat()

with open(DST, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False)

size = os.path.getsize(DST)
print(f"leads={len(leads)}")
print(f"output size: {size/1024/1024:.2f} MB")
print(f"base64 payload: {size*1.333/1024/1024:.2f} MB")
