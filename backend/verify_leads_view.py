# verify_leads_view.py — 验证 industry-leads 接口读数据库
import os, sys, io
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()
from rest_framework.test import APIClient
from apps.users.models import User

out = []
c = APIClient()
u = User.objects.get(username='admin')
c.force_authenticate(u)
r = c.get('/api/keywords/industry-leads')
d = r.json()
out.append('status=%s total=%s source=%s' % (r.status_code, d.get('total'), d.get('source')))
for x in (d.get('results') or [])[:6]:
    out.append('%s|%s|%s|%s|%s' % (x['id'], x['industry'], x['region'], x['intent'], x['scenario'][:16]))
# 过滤测试
r2 = c.get('/api/keywords/industry-leads', {'industry': '法律行业'})
out.append('legal filter total=%s' % r2.json().get('total'))
r3 = c.get('/api/keywords/industry-leads', {'intent': '90'})
out.append('intent>=90 total=%s' % r3.json().get('total'))

with open('verify_leads_view_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('DONE')
