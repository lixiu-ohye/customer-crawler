"""AI 分析服务：需求摘要、语义正负筛查、话术生成、批量重筛"""
import re

from apps.leads.models import Lead
from apps.leads.services import serialize_lead
from apps.crawler.services.intent_scoring import IntentScoring, NEGATIVE_WORDS, POSITIVE_WORDS


class AIAnalysisService:
    """规则引擎版 AI 分析（可平滑替换为大模型 API）"""

    @staticmethod
    def summarize(lead):
        """需求摘要：提取核心诉求"""
        text = f"{lead.title} {lead.content}"
        sentences = re.split(r"[。！？!?；;，,]", text)
        strong = [s.strip() for s in sentences if any(w in s for w in POSITIVE_WORDS) and len(s.strip()) >= 6]
        if strong:
            return " / ".join(strong[:3])
        return text[:80] if text else "无有效内容"

    @staticmethod
    def sentiment_filter(lead, mode="positive"):
        """语义正负筛查：positive 保留正向；negative 标记负向"""
        text = f"{lead.title} {lead.content}"
        neg_hits = [w for w in NEGATIVE_WORDS if w in text]
        pos_hits = [w for w in POSITIVE_WORDS if w in text]
        if mode == "positive":
            keep = len(pos_hits) > 0 and len(neg_hits) == 0
            reason = "正向表达" if keep else ("含负面词: " + "、".join(neg_hits[:5]) if neg_hits else "无明确意图表达")
        else:
            keep = len(neg_hits) > 0
            reason = "负面词: " + "、".join(neg_hits[:5]) if neg_hits else "无负面表达"
        return {"keep": keep, "reason": reason, "pos_hits": pos_hits[:5], "neg_hits": neg_hits[:5]}

    @staticmethod
    def generate_script(lead):
        """话术生成：根据需求/地域/意向生成触达话术"""
        region = lead.region if lead.region and lead.region != "未知地域" else "您所在区域"
        demand = lead.demand if lead.demand != "其他" else "相关服务"
        score = lead.intent_score
        if score >= 60:
            opening = "您好，看到您最近在关注"
            closing = "我们正好提供该服务，可以给您一份详细的方案和报价，方便的话加个联系方式详聊？"
        else:
            opening = "您好，打扰一下，注意到您提到"
            closing = "如果后续有需要，可以随时联系我们，先给您留个资料参考。"
        return {
            "opening": f"{opening}「{demand}」方面的问题",
            "body": f"针对{region}的需求，我们可以提供专业建议与定制方案，已有多个类似客户案例。",
            "closing": closing,
            "full": f"{opening}「{demand}」方面的问题。针对{region}的需求，我们可以提供专业建议与定制方案，已有多个类似客户案例。{closing}",
        }

    @staticmethod
    def rescreen(user, min_score=None, max_count=None):
        """批量重筛：重新打分所有线索，过滤低分"""
        leads = Lead.objects.filter(user=user, is_blacklisted=False)
        if max_count:
            leads = leads[:max_count]
        scorer = IntentScoring()
        updated = 0
        for lead in leads:
            score, _ = scorer.score(
                {"content": lead.content, "title": lead.title,
                 "like_count": lead.like_count, "comment_count": lead.comment_count,
                 "share_count": lead.share_count},
                [], [],
            )
            if min_score is not None and score < min_score:
                lead.status = "filtered"
            else:
                lead.status = "new"
            lead.intent_score = score
            lead.save(update_fields=["intent_score", "status"])
            updated += 1
        return {"updated": updated}
