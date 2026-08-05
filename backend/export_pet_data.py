# -*- coding: utf-8 -*-
"""宠物行业专项数据导出 → frontend/src/api/embed-data.js
策略：
- 宠物线索（tags 或 demand 含"宠物"）全量导出，客户优先
- 非宠物线索只取高意向（intent_score>=60）或 is_customer=True 的
- 控制体积：content 截断 40 字符
"""
import os, sys, json
sys.path.insert(0, r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["PYTHONIOENCODING"] = "utf-8"
import django
django.setup()
from django.apps import apps
Lead = apps.get_model("leads", "Lead")

def lead_to_dict(l):
    return {
        "id": l.id,
        "platform": l.platform or "",
        "item_id": l.item_id or "",
        "title": (l.title or "")[:40],
        "content": (l.content or "")[:40],
        "author": l.author or "",
        "author_id": l.author_id or "",
        "url": l.url or "",
        "region": l.region or "",
        "demand": l.demand or "",
        "intent_score": l.intent_score or 0,
        "intent_label": l.intent_label or "low",
        "tags": l.tags or [],
        "like_count": l.like_count or 0,
        "comment_count": l.comment_count or 0,
        "share_count": l.share_count or 0,
        "publish_time": l.publish_time.strftime("%Y-%m-%d %H:%M:%S") if l.publish_time else "",
        "is_customer": l.is_customer,
        "customer_type": l.customer_type or "",
        "customer_reason": (l.customer_reason or "")[:80],
        "contact_hint": l.contact_hint or "",
        "needs": (l.needs or "")[:80],
    }

all_leads = list(Lead.objects.all())
print("Lead 总数:", len(all_leads))

pet = [l for l in all_leads if (l.tags and any("宠物" in str(t) for t in l.tags)) or "宠物" in (l.demand or "")]
print("宠物线索:", len(pet))
pet_cust = [l for l in pet if l.is_customer is True]
pet_non = [l for l in pet if l.is_customer is not True]
print("  宠物客户:", len(pet_cust), "| 宠物非客户:", len(pet_non))

nonpet = [l for l in all_leads if l not in pet]
nonpet_keep = [l for l in nonpet if (l.intent_score or 0) >= 85][:2000]
print("非宠物高价值保留:", len(nonpet_keep))

# 宠物客户优先排序
pet_cust.sort(key=lambda l: -(l.intent_score or 0))
pet_non.sort(key=lambda l: -(l.intent_score or 0))
nonpet_keep.sort(key=lambda l: -(l.intent_score or 0))

ordered = pet_cust + pet_non + nonpet_keep
print("导出总数:", len(ordered))

data = {
    "exported_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "leads": [lead_to_dict(l) for l in ordered],
}

out_path = r"C:\Users\ZhuanZ（无密码）\.qclaw\workspace\customer-crawler\frontend\src\api\embed-data.js"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("// AUTO-GENERATED real-data (pet-first)\nexport const EMBED_LEADS = ")
    f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    f.write("\n")
size = os.path.getsize(out_path)
print(f"已写入 {out_path}")
print(f"文件大小: {size/1024/1024:.2f} MB")
