# -*- coding: utf-8 -*-
"""GLM 客户筛选器：判断内容发布者是否为「潜在客户」（SAAS 获客机制）

SAAS 获客平台（如探迹、纷享销客）的筛选逻辑：
- 潜在客户 = 发布者本人有真实需求（第一人称：我想/我要/求/咨询/多少钱/怎么办），
  或明确表达购买/服务意向（求推荐、求介绍、找公司、询价、比价、预约）
- 排除：营销号/博主/自媒体（科普、干货、教程、评测、带货、引流）、
  官方账号/机构号、小编搬运、闲聊水帖、新闻资讯、情绪表达（无行动意图）、
  内容只是"提到关键词"但发布者不是客户（如律师科普婚姻法律、博主分享装修心得）

用法:
    from apps.crawler.services.customer_ai_filter import CustomerAIFilter
    f = CustomerAIFilter()
    result = f.classify(title, content, author, platform, industry)  # dict
    result = f.classify_batch(items, industry)  # 批量（自动分组、失败降级）

返回 dict:
    {
      "is_customer": bool,        # 是否潜在客户
      "customer_type": str,       # high/medium/low/none （需求强度）
      "reason": str,              # 简短理由
      "contact_hint": str,        # 联系方式线索（主页/平台ID/无）
      "needs": str,               # 客户需求描述
      "industry": str,            # 判定的行业
    }
"""
import json
import os
import re
import time
from pathlib import Path

# 优先读环境变量 ZAI_API_KEY；否则读 ~/.qclaw/openclaw.json 里的 zai provider
API_KEY = os.environ.get("ZAI_API_KEY", "")
if not API_KEY:
    try:
        cfg = json.loads(Path(os.path.expanduser("~/.qclaw/openclaw.json")).read_text(encoding="utf-8"))
        API_KEY = (cfg.get("models", {}).get("providers", {}).get("zai", {}) or {}).get("apiKey", "")
    except Exception:
        API_KEY = ""

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4.5-air"
MAX_TOKENS = 1024
TIMEOUT = 45
BATCH_SIZE = 12  # 每批条数（控制 token）
MAX_RETRY = 2
_CACHE = {}  # (title, content) -> result 内存缓存


SYSTEM_PROMPT = """你是一个专业的大数据获客系统的客户筛选引擎，负责判断社交媒体内容发布者是否为「潜在客户」。

【判断目标】
潜在客户 = 发布者本人有真实需求，是某项产品/服务的购买决策者或需求方。例如：
- 第一人称真实需求："我家房子要装修，求推荐靠谱的装修公司"、"想做双眼皮，哪个医院好"、"孩子要上小学了，学区房怎么选"
- 明确询价/比价："装修120平大概多少钱"、"植发一个单位多少钱"、"月嫂一个月多少钱"
- 求推荐/求介绍："求推荐靠谱的律师"、"有没有好的搬家公司"、"想找家政阿姨"
- 描述自身困扰并寻求解决："油烟机坏了不知道怎么修"、"最近掉头发严重怎么办"、"猫总是生病，宠物医院哪家好"

【排除对象】（不是客户）
- 营销号/自媒体/博主：科普、干货分享、教程、评测、攻略、经验分享、带货、引流、求关注
- 官方/机构/媒体账号：新闻、政策解读、行业分析、热点评论
- 小编搬运/资讯号：聚合内容、无个人真实需求
- 闲聊/水帖/段子：无行动意图的情绪表达
- 内容只是"提到关键词"但发布者不是客户（如律师科普婚姻法律、装修博主分享设计心得、医生科普健康知识）

【输出格式】
必须输出严格的 JSON 数组，每项对应一条内容，字段：
{"is_customer": true/false, "customer_type": "high|medium|low|none", "reason": "简短理由", "contact_hint": "homepage|platform_id|text|none", "needs": "客户需求一句话", "industry": "行业名"}
- is_customer: 是否潜在客户
- customer_type: high=强烈需求（求购/询价/预约/急），medium=明确需求（想/要/找/咨询），low=潜在需求（考虑/了解/观望），none=非客户
- contact_hint: 发布者主页链接(homepage)/平台ID(platform_id)/文中留了联系方式(text)/无(none)
- industry: 客户所属行业（从内容判断，如：装修家居、法律服务、医美健康、家政服务、汽车服务、教育培训、宠物服务、金融理财、企业服务、电商零售、本地生活、房产、婚庆、口腔、工程、其他）
- reason: 5-20字中文理由

严格要求：
1. 只输出 JSON 数组，不要任何其他文字、解释或 markdown 代码块
2. 宁缺毋滥：不确定的一律 is_customer=false（宁可少收，不要混入非客户）
3. 不要编造联系方式，contact_hint 只能基于内容里实际出现的信息"""


class CustomerAIFilter:
    """GLM 客户筛选器（带规则降级）"""

    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEY
        self.enabled = bool(self.api_key)
        # 强规则快速路径：明显的营销号/博主特征
        self.MARKETING_RE = re.compile(r"关注我|点赞收藏|转发抽奖|免费领取|限时优惠|点击下方|评论区|私信我(领取|获取|报名|进群|发你|发资料)|加微信|扫码|领取资料|直播间|橱窗|小黄车|购物车|主页置顶|商务合作|广告位|测评|探店打卡|干货|教程|攻略|避坑指南|经验分享|必看|速通|一定要收藏|收藏好|转发给|提醒大家|请注意|注意了|戳我|帮你报价|10秒|报价方案|计算器|一键|9张图|几张图|这篇文章|看完这篇|建议收藏|避坑|踩雷|种草|安利|团购|拼团|预约|到店|门店|线下体验|免费设计|免费量房|免费上门|领取|进群|添加微信|联系方式在|主页有|私我|普通人|一生要花|大家注意看|给大?科普|科普一下|涨知识|生活小妙招|冷知识|实用帖|干货满满")
        # 服务提供者特征：律师/医生/商家自我介绍、服务范围、接单说明
        self.PROVIDER_RE = re.compile(r"(本(人|律师|所|院|店|公司)|我是(律师|医生|老师|商家|店主|顾问)|从事.{0,6}(法律|医疗|装修|家政|教育)|专注.{0,8}(法律|婚姻|医美|装修|教育)|执业|律所|主任律师|资深律师|代理费|服务范围|接单|预约咨询|免费咨询|限时免费|提供.{0,6}服务|负责.{0,6}业务|从业.{0,6}年|#.*律?#|的微博|抖音号|小红书号|欢迎咨询|欢迎合作)")
        # 弱提供者信号：命中则交给 GLM（避免误判服务提供者为客户）
        self.WEAK_PROVIDER_RE = re.compile(r"(我的初心|给大家提供|免费.{0,4}咨询|free|公益咨询|帮助大家|有需要的|找我|来找我|私信我咨询|法律咨询)|(咨询|推荐|介绍|合作).{0,8}(我|本)人")
        self.BLOGGER_RE = re.compile(r"博主|小编|自媒体|运营|账号|up主|作者|分享|创作|粉丝|流量|涨粉|变现")

    # ---------- 规则快速路径（省 token） ----------
    STRONG_NEED_RE = re.compile(r"(求推荐|求介绍|求购|找.{0,6}(公司|师傅|医院|机构|律师|阿姨|设计师|装修|搬家|家政|保洁|月嫂)|多少钱|怎么收费|怎么弄|哪里有|哪里(好|靠谱|便宜)|有没有(推荐|靠谱|好的)|想找|想买|想了解|要装修|准备装|打算(买|做|去|找)|急(需|找|求)|预约|上门|报个价|给个价|预算|请问.{0,10}(多少钱|怎么)|求.{0,4}(推荐|介绍|联系))")

    def _rule_fast_path(self, text):
        """快速路径：返回 'customer' / 'not_customer' / None（None=交给 GLM）
        1. 服务提供者特征 → not_customer（律师/医生/商家自述）
        2. 强需求词 → customer（直接判定，省 token）
        3. 强营销/科普信号 → not_customer
        4. 其余 → None（模糊，交给 GLM）
        """
        if not text:
            return "not_customer"
        if self.PROVIDER_RE.search(text):
            return "not_customer"
        if self.MARKETING_RE.search(text):
            return "not_customer"
        if self.STRONG_NEED_RE.search(text):
            # 同时有弱提供者信号 → 交给 GLM 判断（可能是服务提供者自述）
            if self.WEAK_PROVIDER_RE.search(text):
                return None
            return "customer"
        if re.search(r"(我觉得|我认为|分享.{0,6}(心得|经验)|正能量|提醒.{0,4}朋友|小编|博主|朋友们|姐妹们|网友们)", text):
            return "not_customer"
        return None

    # ---------- GLM 调用 ----------
    def _call_glm(self, items):
        """items: [{title, content, author, platform}] → list[dict] 或 None"""
        if not self.enabled:
            return None
        payload = []
        for it in items:
            payload.append({
                "title": (it.get("title") or "")[:60],
                "content": (it.get("content") or "")[:300],
                "author": (it.get("author") or "")[:20],
                "platform": it.get("platform", ""),
            })
        body = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "请判断以下内容发布者是否为潜在客户：\n" + json.dumps(payload, ensure_ascii=False)},
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.2,
        }
        last_err = None
        for attempt in range(MAX_RETRY + 1):
            try:
                import urllib.request
                req = urllib.request.Request(
                    API_URL,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key},
                )
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                # 兼容 reasoning 模型：content 为空时尝试 reasoning_content
                if not content:
                    content = (data.get("choices") or [{}])[0].get("message", {}).get("reasoning_content", "")
                # 提取 JSON 数组
                arr = self._extract_json(content)
                if arr is not None and len(arr) == len(items):
                    return arr
                if arr is not None:
                    return arr
                last_err = f"parse fail: {content[:100]}"
            except Exception as e:
                last_err = str(e)
                time.sleep(2 * (attempt + 1))
        if last_err:
            return None

    @staticmethod
    def _extract_json(content):
        """从 GLM 输出中提取 JSON 数组"""
        if not content:
            return None
        s = content.strip()
        # 去掉 markdown 代码块
        if s.startswith("```"):
            s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
            s = re.sub(r"\n?```$", "", s)
        try:
            return json.loads(s)
        except Exception:
            pass
        # 找第一个 [ 到最后一个 ]
        try:
            i, j = s.find("["), s.rfind("]")
            if i >= 0 and j > i:
                return json.loads(s[i:j + 1])
        except Exception:
            pass
        return None

    # ---------- 对外接口 ----------
    def classify(self, title, content, author="", platform="", industry=""):
        """单条分类，返回 dict"""
        key = (title or "")[:80] + "|" + (content or "")[:200]
        if key in _CACHE:
            return _CACHE[key]
        result = self.classify_batch([{"title": title, "content": content, "author": author, "platform": platform}], industry)
        out = result[0] if result else self._fallback(title, content)
        _CACHE[key] = out
        return out

    def classify_batch(self, items, industry=""):
        """批量分类。返回与 items 等长的 dict 列表；GLM 失败时逐条规则降级。"""
        results = {}
        pending = []
        # 规则快速路径（省 token）
        for idx, it in enumerate(items):
            text = (it.get("title") or "") + " " + (it.get("content") or "")
            fast = self._rule_fast_path(text)
            if fast == "customer":
                results[idx] = self._rule_result(text, industry, force_customer=True)
            elif fast == "not_customer":
                results[idx] = self._rule_result(text, industry)
            else:
                pending.append((idx, it))
        # GLM 处理未决的（保留原始下标）
        if pending and self.enabled:
            for b in range(0, len(pending), BATCH_SIZE):
                chunk = pending[b:b + BATCH_SIZE]
                arr = self._call_glm([it for _, it in chunk])
                if arr:
                    for (idx, it), r in zip(chunk, arr):
                        results[idx] = self._normalize(r, it, industry)
                else:
                    for idx, it in chunk:
                        text = (it.get("title") or "") + " " + (it.get("content") or "")
                        results[idx] = self._rule_result(text, industry)
        # 未覆盖的（无 GLM key 且非 fast）→ 规则兜底
        for idx, it in pending:
            if idx not in results:
                text = (it.get("title") or "") + " " + (it.get("content") or "")
                results[idx] = self._rule_result(text, industry)
        # 按原始顺序返回
        return [results.get(i, self._fallback(items[i].get("title", "") if i < len(items) else "", "")) for i in range(len(items))]

    def _normalize(self, r, it, industry):
        """标准化 GLM 返回"""
        if not isinstance(r, dict):
            return self._fallback("", "")
        is_customer = bool(r.get("is_customer"))
        ctype = str(r.get("customer_type") or "none").lower()
        if ctype not in ("high", "medium", "low", "none"):
            ctype = "medium" if is_customer else "none"
        return {
            "is_customer": is_customer,
            "customer_type": ctype,
            "reason": str(r.get("reason") or "")[:50],
            "contact_hint": str(r.get("contact_hint") or "none")[:30],
            "needs": str(r.get("needs") or "")[:100],
            "industry": str(r.get("industry") or industry or "")[:30],
        }

    def _rule_result(self, text, industry="", force_customer=False):
        """规则降级结果（保守：默认非客户；force_customer 时判客户）"""
        if force_customer:
            m = self.STRONG_NEED_RE.search(text)
            return {
                "is_customer": True, "customer_type": "medium",
                "reason": "规则命中强需求词", "contact_hint": "platform_id",
                "needs": m.group(0) if m else "", "industry": industry,
            }
        return {
            "is_customer": False, "customer_type": "none",
            "reason": "规则判定非客户", "contact_hint": "none",
            "needs": "", "industry": industry,
        }

    def _fallback(self, title, content):
        """完全失败时的兜底（保守：非客户，避免误收）"""
        return {
            "is_customer": False, "customer_type": "none",
            "reason": "筛选失败", "contact_hint": "none",
            "needs": "", "industry": "",
        }


def filter_leads(items, industry=""):
    """便捷入口：items 列表 → 返回 (customers, non_customers)
    items: [{title, content, author, platform}]（其他字段透传）
    """
    f = CustomerAIFilter()
    results = f.classify_batch(items, industry)
    customers, non_customers = [], []
    for it, r in zip(items, results):
        it["_customer"] = r
        if r.get("is_customer"):
            customers.append(it)
        else:
            non_customers.append(it)
    return customers, non_customers
