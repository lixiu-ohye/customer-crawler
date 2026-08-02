# -*- coding: utf-8 -*-
"""v2 内容质量过滤器：收紧误杀，精准过滤小说/网文/无关内容

v1 教训：单独出现「娱乐圈/疯批/ABO」等词会误杀真实需求
v2 原则：
1. 网文特征需要「组合证据」才判垃圾（如章节标记+对话体、书单格式+作者）
2. 强结构特征（章节标记、网文平台名）直接判
3. 真实需求保护：命中行业主词/长尾词 → 除非证据确凿（章节+平台），否则放行
4. 叙述体长文但无行业词 → 判垃圾（水帖/故事）
"""
import re

# ============ 一级：确凿网文/无关（组合证据，几乎不误杀） ============
# 网文章节标记 + 对话体（小说实锤）
CHAPTER_PAT = re.compile(r"第\s*[一二三四五六七八九十百千万零〇0-9]+\s*[章节回卷]")
DIALOG_PAT = re.compile(r"(?:[“\"「『]|他说|她说|我[说问道]|想了想说)")

# 网文平台名（实锤）
PLATFORM_PAT = re.compile(r"起点中文网|晋江文学城|晋江|番茄小说|纵横中文网|飞卢|17k小说网|红袖添香|潇湘书院|七猫小说|塔读|刺猬猫|菠萝包|轻之文库|SF轻小说")

# 书单/推书格式（实锤）
BOOKLIST_PAT = re.compile(r"(?:书单|推书|求书|好书推荐|小说推荐|安利.{0,6}(?:小说|文))")

# 漫画/影视/游戏无关
COMIC_PAT = re.compile(r"(?:韩漫|日漫|国漫|漫画(?:分享|推荐|解说)|动漫(?:推荐|解说)|耽美|纯爱|双男主|同人)")
# 游戏无关：需要强游戏上下文，避免误伤（内测/段位/皮肤等在正常语境常见）
GAME_PAT = re.compile(r"新地图[:：]|版本更新公告|游戏更新公告|抽卡|角色强度|开服|公测|副本攻略|排位赛|吃鸡|王者荣耀|原神|明日方舟|崩坏|steam|Steam|PC版|手游[^，。]*上线|游戏[^，。]*攻略|段位数据|上分|掉段")
# 弱游戏词需配合强游戏上下文：
# - 皮肤 → 游戏皮肤/抽皮肤/皮肤系统
# - 内测 → 游戏内测/开测
# - 玩家 → 游戏玩家
GAME_WEAK_PAT = re.compile(r"游戏[^，。]{0,10}(?:皮肤|内测|玩家)|(?:皮肤|内测|玩家)[^，。]{0,10}(?:系统|活动)")
# 段位/上分等强游戏词直接命中（防“位置”子串：段位/排位后不接“置”）
GAME_STRONG_PAT = re.compile(r"段位(?!置)|上分|掉段|排位(?!置)")

# 小说推荐格式：《书名》by 作者 + 标签
NOVEL_REC_PAT = re.compile(r"《[^》]{2,20}》\s*by\s*[\u4e00-\u9fa5\w]{1,20}")

# ============ 二级：需组合证据 ============
# 网文套路词（需配合书名号/章节/作者等）
TROPE_WORDS = ["重生", "穿越", "修仙", "修真", "赘婿", "战神", "龙王", "医仙", "帝尊", "老祖", "系统流", "金手指", "打脸", "爽文", "虐文"]
# 网文标签词（出现 2 个以上才提示）
TAG_WORDS = ["ABO", "娱乐圈", "强制爱", "生子", "疯批", "破镜重圆", "先婚后爱", "追妻火葬场", "he", "be", "甜宠", "姐弟恋"]

# 叙述体特征（长文无行业词时用）
NARRATIVE_PAT = re.compile(r"(?:那天下午|那天晚上|记得那年|想当年|从小时候|他说|她说|我说|心里想|眼泪|忍不住)")

# 营销/低价值特征
MARKETING_PAT = re.compile(r"关注我|点赞收藏|转发抽奖|免费领取|限时优惠|点击下方|链接在评论区|私信我|加微信|扫码|领取资料|0\.99|9\.9")
TUTORIAL_PAT = re.compile(r"教程|干货|攻略|测评|避坑|经验分享|收藏起来|必看|速通|小妙招|一分钟")

# 行业词（需求保护）
def _load_industry_words():
    try:
        from apps.keywords.industry_library import INDUSTRY_LIBRARY, GLOBAL_NEGATIVE_WORDS
        words = set()
        for conf in INDUSTRY_LIBRARY.values():
            for w in conf.get("mainWords", []) + conf.get("longTailWords", []):
                if len(w) >= 2:
                    words.add(w)
        return words, set(GLOBAL_NEGATIVE_WORDS)
    except Exception:
        return set(), set()

INDUSTRY_WORDS, GLOBAL_NEGATIVE = _load_industry_words()


def has_industry_word(text):
    return any(w and w in text for w in INDUSTRY_WORDS)


def classify_content(title, content):
    """返回 (action, reason)
    action: keep / junk / low_value
    """
    text = (title or "") + " " + (content or "")
    if not text.strip():
        return "junk", "空内容"

    has_ind = has_industry_word(text)

    # ===== 一级确凿证据 =====
    # 网文平台名（无论是否行业词都删，如"晋江"出现在消防维保里是地名误判，需谨慎）
    m = PLATFORM_PAT.search(text)
    if m and m.group(0) != "晋江":
        return "junk", f"网文平台({m.group(0)})"
    # 晋江特殊处理：仅当上下文像网文（书名号/章节）才判
    if "晋江" in text and (CHAPTER_PAT.search(text) or BOOKLIST_PAT.search(text)):
        return "junk", "网文平台(晋江)"

    # 章节标记 + 对话体 → 小说实锤
    if CHAPTER_PAT.search(text) and DIALOG_PAT.search(text):
        return "junk", "章节+对话体"

    # 书单/推书格式 + 书名号 → 小说推荐实锤
    if BOOKLIST_PAT.search(text) and re.search(r"《[^》]+》", text):
        return "junk", "书单推书"

    # 小说推荐格式《书名》by 作者
    if NOVEL_REC_PAT.search(text):
        return "junk", "小说推荐"

    # 漫画/游戏（除非内容明显是真实行业需求）
    if COMIC_PAT.search(text) and not has_ind:
        return "junk", "漫画无关"
    if GAME_PAT.search(text) and not has_ind:
        return "junk", "游戏无关"
    # 弱游戏词（皮肤/内测/玩家）需强游戏上下文；强游戏词（段位/上分/排位）直接命中
    if GAME_STRONG_PAT.search(text) and not has_ind:
        return "junk", "游戏无关(段位)"
    if GAME_WEAK_PAT.search(text) and not has_ind:
        return "junk", "游戏无关(弱词)"

    # ===== 二级：组合证据 =====
    # 网文套路词：需同时命中书名号或"主角/第X章"
    trope_hits = [w for w in TROPE_WORDS if w in text]
    if len(trope_hits) >= 2 and (re.search(r"《[^》]+》", text) or "主角" in text):
        return "junk", f"网文套路({','.join(trope_hits[:3])})"

    # 网文标签词 ≥2 且无行业词
    tag_hits = [w for w in TAG_WORDS if w.lower() in text.lower()]
    if len(tag_hits) >= 2 and not has_ind:
        return "junk", f"网文标签({','.join(tag_hits[:3])})"

    # 叙述体长文（>500字）：不再直接删，降为 low_value（可能是真实经历分享，也可能是故事）
    # 仅当同时满足：无行业词 + 无需求场景词 + 高叙述特征时标记为低价值
    if len(content or "") > 500 and not has_ind:
        narr_hits = len(NARRATIVE_PAT.findall(text))
        if narr_hits >= 3:
            return "low_value", f"叙述体长文({narr_hits})"

    # ===== 低价值（不删，标记） =====
    if MARKETING_PAT.search(text):
        return "low_value", "营销内容"
    if TUTORIAL_PAT.search(text):
        return "low_value", "教程/干货"

    # 全局否定词
    neg_hits = [w for w in GLOBAL_NEGATIVE if w and w in text]
    if neg_hits:
        return "low_value", f"否定词({','.join(neg_hits[:3])})"

    return "keep", "正常"


def filter_batch(leads):
    """leads: [{id,title,content}] → (kept, junked, low)"""
    kept, junked, low = [], [], []
    for item in leads:
        action, reason = classify_content(item.get("title", ""), item.get("content", ""))
        if action == "junk":
            junked.append((item, reason))
        elif action == "low_value":
            low.append((item, reason))
        else:
            kept.append(item)
    return kept, junked, low
