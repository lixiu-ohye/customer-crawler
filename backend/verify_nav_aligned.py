# -*- coding: utf-8 -*-
"""对齐验证：industry-nav / industry-tree / industry-leads 后端真实返回（force_authenticate 版）"""
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from apps.keywords.views.industry_nav import (
    IndustryNavView, IndustryTreeView, IndustryLeadsView, IndustryRegionsView,
)
from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate

factory = APIRequestFactory()
admin = User.objects.filter(username="admin").first()
if not admin:
    print("FAIL: admin user not found")
    sys.exit(1)

PASS = FAIL = 0
def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"OK: {name} {extra}")
    else:
        FAIL += 1
        print(f"FAIL: {name} {extra}")

def call(view_cls, method, path):
    req = getattr(factory, method)(path)
    force_authenticate(req, user=admin)
    return view_cls.as_view()(req)

# 1. industry-nav 列表
resp = call(IndustryNavView, "get", "/api/keywords/industry-nav")
data = resp.data
check("nav-list has results", "results" in data, f"keys={list(data.keys())}")
inds = data["results"]["industries"]
check("nav-list 13 industries", len(inds) == 13, f"count={len(inds)}")
names = [i["name"] for i in inds]
check("nav-list has 法律行业", "法律行业" in names)
check("nav-list has cities", "cities" in data["results"], f"cities={data['results']['cities'][:3]}")
check("nav-list item fields", all(k in inds[0] for k in ("id", "name", "description", "preview")))

# 2. industry-nav 单行业
resp = call(IndustryNavView, "get", "/api/keywords/industry-nav?industry=%E6%B3%95%E5%BE%8B%E8%A1%8C%E4%B8%9A")
data = resp.data
check("nav-single has results", "results" in data)
r = data["results"]
check("nav-single mainWords", len(r.get("mainWords", [])) == 10, f"n={len(r.get('mainWords', []))}")
check("nav-single globalNegative", len(r.get("globalNegativeWords", [])) >= 10)

# 3. industry-tree 法律行业
resp = call(IndustryTreeView, "get", "/api/keywords/industry-tree?industry=%E6%B3%95%E5%BE%8B%E8%A1%8C%E4%B8%9A")
data = resp.data
tree = data["results"]["tree"]
check("tree legal 10 fields", len(tree) == 10, f"n={len(tree)}")
check("tree 婚姻家庭 has fields", "fields" in tree.get("婚姻家庭", {}))
ff = tree["婚姻家庭"]["fields"]
check("tree 婚姻家庭 fields", "离婚纠纷" in ff, f"keys={list(ff.keys())}")
sc = ff["离婚纠纷"]["scenarios"]
check("tree scenarios", "离婚财产分割" in sc, f"keys={list(sc.keys())}")
check("tree needs", len(ff["离婚纠纷"].get("needs", [])) >= 2)

# 4. industry-tree 其他行业（装修家居）
resp = call(IndustryTreeView, "get", "/api/keywords/industry-tree?industry=%E8%A3%85%E4%BF%AE%E5%AE%B6%E5%B1%85")
data = resp.data
tree = data["results"]["tree"]
check("tree 装修家居 generated", len(tree) >= 3, f"n={len(tree)}")

# 5. industry-leads 过滤
resp = call(IndustryLeadsView, "get", "/api/keywords/industry-leads?industry=%E6%B3%95%E5%BE%8B%E8%A1%8C%E4%B8%9A&intent=90")
data = resp.data
check("leads legal intent>=90", len(data["results"]) >= 3, f"n={len(data['results'])}")
resp = call(IndustryLeadsView, "get", "/api/keywords/industry-leads")
check("leads all", len(resp.data["results"]) >= 8, f"n={len(resp.data['results'])}")

# 6. industry-regions
resp = call(IndustryRegionsView, "get", "/api/keywords/industry-regions")
data = resp.data
check("regions hotspots", "hotspots" in data["results"], f"keys={list(data['results'].keys())}")
check("regions 7 hotspots", len(data["results"]["hotspots"]) == 7, f"n={len(data['results']['hotspots'])}")

print(f"\n=== PASS={PASS} FAIL={FAIL} ===")
sys.exit(0 if FAIL == 0 else 1)
