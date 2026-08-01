"""
客户画像和需求预测模块
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class CustomerProfiler:
    """客户画像构建器"""
    
    # 客户类型定义
    CLUSTER_LABELS = {
        0: '活跃型客户',
        1: '潜在型客户',
        2: '普通型客户',
        3: '沉默型客户'
    }
    
    # 关键词权重（用于需求预测）
    KEYWORD_WEIGHTS = {
        '医疗': 0.9, '医院': 0.9, '诊疗': 0.85, '疫苗': 0.8, '手术': 0.85,
        '美容': 0.8, '洗澡': 0.7, '造型': 0.75, 'SPA': 0.7, '护理': 0.75,
        '用品': 0.7, '食品': 0.75, '玩具': 0.6, '零食': 0.65, '窝': 0.5,
        '寄养': 0.85, '托管': 0.8, '训练': 0.85, '行为': 0.7, '摄影': 0.6,
        '保险': 0.8, '殡葬': 0.7, '健康': 0.8, '检查': 0.75, '咨询': 0.7
    }
    
    # 需求推荐模板
    NEED_TEMPLATES = {
        '活跃型客户': [
            {'need': '高端宠物服务', 'probability': 0.8, 'reason': '活跃度高，可能追求高品质服务'},
            {'need': '宠物健康咨询', 'probability': 0.7, 'reason': '关注宠物健康'},
            {'need': '宠物社交活动', 'probability': 0.6, 'reason': '喜欢分享互动'}
        ],
        '潜在型客户': [
            {'need': '宠物入门服务', 'probability': 0.9, 'reason': '新用户，需引导'},
            {'need': '宠物知识培训', 'probability': 0.8, 'reason': '需要了解养宠知识'},
            {'need': '宠物用品推荐', 'probability': 0.7, 'reason': '需要购置基础用品'}
        ],
        '普通型客户': [
            {'need': '常规宠物护理', 'probability': 0.8, 'reason': '有稳定需求'},
            {'need': '宠物用品购买', 'probability': 0.7, 'reason': '日常消费'},
            {'need': '宠物美容服务', 'probability': 0.6, 'reason': '常规需求'}
        ],
        '沉默型客户': [
            {'need': '宠物关怀提醒', 'probability': 0.9, 'reason': '需要激活'},
            {'need': '宠物健康检查', 'probability': 0.8, 'reason': '预防性需求'},
            {'need': '宠物保险推荐', 'probability': 0.7, 'reason': '降低风险'}
        ]
    }
    
    def __init__(self):
        self.db = None  # 可注入数据库连接
    
    def set_database(self, db):
        """设置数据库连接"""
        self.db = db
    
    def build_customer_profile(self, user_data: Dict) -> Dict:
        """
        根据用户行为数据构建客户画像
        
        参数 user_data 包含:
        - platforms: 活跃平台列表
        - sentiments: 情感倾向列表
        - keywords: 关键词列表
        - engagement: 互动数据 (likes, comments, shares)
        - activity_dates: 活动日期列表
        - content_lengths: 内容长度列表
        """
        # 1. 计算平台多样性
        platforms = user_data.get('platforms', [])
        platform_diversity = len(set(platforms)) if platforms else 0
        
        # 2. 计算主要情感倾向
        sentiments = user_data.get('sentiments', [])
        main_sentiment = 'neutral'
        if sentiments:
            sentiment_counts = defaultdict(int)
            for s in sentiments:
                sentiment_counts[s] += 1
            main_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # 3. 计算互动指数
        engagement = user_data.get('engagement', {})
        engagement_index = (
            engagement.get('likes', 0) * 1 + 
            engagement.get('comments', 2) + 
            engagement.get('shares', 3)
        )
        
        # 4. 计算活跃度
        activity_dates = user_data.get('activity_dates', [])
        last_active_days = 0
        if activity_dates:
            try:
                latest_date = max(datetime.fromisoformat(d) for d in activity_dates)
                last_active_days = (datetime.now() - latest_date).days
            except:
                last_active_days = 30
        
        # 5. 计算文本特征
        content_lengths = user_data.get('content_lengths', [])
        avg_content_length = np.mean(content_lengths) if content_lengths else 0
        
        # 6. 关键词多样性
        keywords = user_data.get('keywords', [])
        keyword_diversity = len(set(keywords)) if keywords else 0
        
        # 7. 确定客户类型（基于规则）
        customer_type = self._classify_customer(
            engagement_index=engagement_index,
            platform_diversity=platform_diversity,
            last_active_days=last_active_days,
            keyword_diversity=keyword_diversity
        )
        
        # 8. 生成画像描述
        profile_text = self._generate_profile_text({
            'customer_type': customer_type,
            'main_sentiment': main_sentiment,
            'platforms': platforms,
            'engagement_index': engagement_index,
            'last_active_days': last_active_days,
            'keywords': keywords[:5]
        })
        
        return {
            'platforms': list(set(platforms)),
            'main_sentiment': main_sentiment,
            'keywords': list(set(keywords))[:10],
            'engagement_index': engagement_index,
            'last_active_days': last_active_days,
            'platform_diversity': platform_diversity,
            'keyword_diversity': keyword_diversity,
            'avg_content_length': round(avg_content_length, 1),
            'customer_type': customer_type,
            'profile_text': profile_text,
            'created_at': datetime.now().isoformat()
        }
    
    def _classify_customer(self, engagement_index: int, platform_diversity: int, 
                          last_active_days: int, keyword_diversity: int) -> str:
        """基于特征分类客户类型"""
        # 活跃度得分
        activity_score = 0
        if engagement_index > 100:
            activity_score += 2
        elif engagement_index > 50:
            activity_score += 1
        
        if platform_diversity >= 3:
            activity_score += 1
        
        if last_active_days < 7:
            activity_score += 2
        elif last_active_days < 30:
            activity_score += 1
        
        if keyword_diversity >= 5:
            activity_score += 1
        
        # 分类
        if activity_score >= 5:
            return self.CLUSTER_LABELS[0]  # 活跃型
        elif activity_score >= 3:
            return self.CLUSTER_LABELS[1]  # 潜在型
        elif activity_score >= 1:
            return self.CLUSTER_LABELS[2]  # 普通型
        else:
            return self.CLUSTER_LABELS[3]  # 沉默型
    
    def _generate_profile_text(self, data: Dict) -> str:
        """生成客户画像描述"""
        text = f"这是一个{data['customer_type']}，"
        text += f"最近活跃于{data['last_active_days']}天前，"
        
        if data['platforms']:
            text += f"主要在{', '.join(data['platforms'][:3])}等平台活跃，"
        
        text += f"情感倾向为{data['main_sentiment']}，"
        text += f"互动指数为{data['engagement_index']}。"
        
        if data['keywords']:
            text += f"关注的关键词包括：{', '.join(data['keywords'][:5])}。"
        
        return text
    
    def predict_needs(self, profile: Dict) -> List[Dict]:
        """预测客户需求"""
        customer_type = profile.get('customer_type', '普通型客户')
        keywords = profile.get('keywords', [])
        
        # 获取基础推荐
        needs = self.NEED_TEMPLATES.get(customer_type, self.NEED_TEMPLATES['普通型客户']).copy()
        
        # 根据关键词调整概率
        for need in needs:
            for keyword in keywords:
                for kw, weight in self.KEYWORD_WEIGHTS.items():
                    if kw in keyword:
                        need['probability'] = min(1.0, need['probability'] * weight)
                        need['reason'] = f"关注{data.get('main_sentiment', '宠物行业')}相关话题"
                        break
        
        # 按概率排序
        needs.sort(key=lambda x: x['probability'], reverse=True)
        
        return needs[:5]
    
    def get_similar_customers(self, target_profile: Dict, all_profiles: List[Dict], 
                              limit: int = 5) -> List[Dict]:
        """获取相似客户"""
        if not all_profiles:
            return []
        
        similar_customers = []
        
        target_platforms = set(target_profile.get('platforms', []))
        target_keywords = set(target_profile.get('keywords', []))
        
        for profile in all_profiles:
            if profile.get('user_id') == target_profile.get('user_id'):
                continue
            
            # 计算相似度
            similarity = 0.0
            
            # 平台相似度 (30%)
            profile_platforms = set(profile.get('platforms', []))
            if target_platforms and profile_platforms:
                platform_sim = len(target_platforms & profile_platforms) / len(target_platforms | profile_platforms)
                similarity += platform_sim * 0.3
            
            # 关键词相似度 (40%)
            profile_keywords = set(profile.get('keywords', []))
            if target_keywords and profile_keywords:
                keyword_sim = len(target_keywords & profile_keywords) / len(target_keywords | profile_keywords)
                similarity += keyword_sim * 0.4
            
            # 情感相似度 (30%)
            if target_profile.get('main_sentiment') == profile.get('main_sentiment'):
                similarity += 0.3
            
            similar_customers.append({
                'user_id': profile.get('user_id'),
                'customer_type': profile.get('customer_type'),
                'similarity': round(similarity, 3)
            })
        
        # 按相似度排序
        similar_customers.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_customers[:limit]


# 单例
_customer_profiler = None


def get_customer_profiler() -> CustomerProfiler:
    """获取客户画像实例"""
    global _customer_profiler
    if _customer_profiler is None:
        _customer_profiler = CustomerProfiler()
    return _customer_profiler