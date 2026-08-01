"""
深度学习情感分析模块
使用规则+词典的轻量级方案（生产环境可替换为TensorFlow/Keras模型）
"""
import re
import logging
from typing import Dict, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class DeepSentimentAnalyzer:
    """
    情感分析器
    使用规则+词典方法，轻量快速
    生产环境可集成 TensorFlow/Keras 深度学习模型
    """
    
    # 正面情感词典
    POSITIVE_WORDS = {
        # 宠物行业正面词
        '可爱', '聪明', '漂亮', '健康', '活泼', '粘人', '忠诚', '温顺', '友好', '贴心',
        '喜欢', '爱', '开心', '快乐', '幸福', '满足', '欣慰', '感动', '惊喜', '完美',
        '推荐', '优质', '专业', '负责', '耐心', '细心', '周到', '性价比', '划算', '值得',
        '方便', '快捷', '高效', '干净', '整洁', '舒适', '温馨', '舒适', '高端', '品质',
        '好评', '点赞', '棒', '赞', '优秀', '出色', '惊艳', '良心', '靠谱', '放心'
    }
    
    # 负面情感词典
    NEGATIVE_WORDS = {
        # 宠物行业负面词
        '可怕', '讨厌', '恶心', '失望', '生气', '愤怒', '伤心', '难过', '害怕', '担心',
        '后悔', '坑', '骗', '黑心', '无良', '敷衍', '不专业', '差', '烂', '垃圾',
        '贵', '不值', '亏', '宰客', '欺骗', '隐瞒', '虚假', '夸大', '货不对板', '售后差',
        '态度差', '不耐烦', '冷漠', '粗心', '失误', '延误', '迟到', '不守时', '不靠谱',
        '差评', '无语', '吐槽', '避雷', '黑榜', '投诉', '纠纷', '维权', '曝光', '警惕'
    }
    
    # 程度副词权重
    DEGREE_WORDS = {
        '非常': 1.5, '特别': 1.5, '极其': 1.8, '十分': 1.5, '特别': 1.5,
        '很': 1.2, '比较': 1.0, '相当': 1.3, '太': 1.5, '真': 1.2,
        '稍微': 0.8, '略': 0.8, '有点': 0.8, '一般': 0.5
    }
    
    # 否定词
    NEGATION_WORDS = {'不', '没', '无', '非', '未', '别', '莫', '勿', '休'}
    
    def __init__(self):
        self.is_trained = True  # 词典方法无需训练
        self.model_type = 'rule_based'  # 可切换为 'deep_learning'
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        if not text:
            return ""
        
        # 转小写
        text = text.lower()
        
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除@用户名
        text = re.sub(r'@[\w]+', '', text)
        
        # 去除表情符号
        text = re.sub(r'\[.*?\]', '', text)
        
        # 去除特殊字符，保留中文、英文、数字
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # 合并空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_words(self, text: str) -> List[str]:
        """提取词语（简单分词）"""
        # 简单处理：按字符级别+常见词组
        words = []
        
        # 尝试匹配常见词组
        patterns = [
            '宠物医院', '宠物医生', '宠物美容', '宠物洗澡', '宠物用品', '宠物食品',
            '宠物寄养', '宠物训练', '宠物殡葬', '宠物保险', '宠物体检', '宠物疫苗',
            '货不对板', '态度差', '售后差', '性价比', '值得推荐', '非常不错',
            '非常满意', '非常可爱', '特别专业', '特别耐心', '太贵了', '不推荐'
        ]
        
        for pattern in patterns:
            if pattern in text:
                words.append(pattern)
        
        # 剩余字符作为单字处理
        for char in text:
            if char.strip():
                words.append(char)
        
        return words
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        情感分析主方法
        返回: {'sentiment': 'positive/neutral/negative', 'score': float, 'confidence': float}
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        # 预处理
        cleaned_text = self.preprocess_text(text)
        words = self._extract_words(cleaned_text)
        
        # 计算情感得分
        positive_score = 0.0
        negative_score = 0.0
        matched_words = {'positive': [], 'negative': []}
        
        for i, word in enumerate(words):
            # 检查程度副词
            degree = 1.0
            if i > 0 and words[i-1] in self.DEGREE_WORDS:
                degree = self.DEGREE_WORDS[words[i-1]]
            
            # 检查否定词
            is_negated = False
            if i > 1 and words[i-1] in self.NEGATION_WORDS:
                is_negated = True
            
            # 匹配情感词
            if word in self.POSITIVE_WORDS:
                score = 1.0 * degree
                if is_negated:
                    score = -score * 0.5  # 否定正面词转为弱负面
                positive_score += score
                matched_words['positive'].append(word)
            
            elif word in self.NEGATIVE_WORDS:
                score = 1.0 * degree
                if is_negated:
                    score = -score * 0.5  # 否定负面词转为弱正面
                negative_score += score
                matched_words['negative'].append(word)
        
        # 计算最终得分
        total = positive_score + negative_score
        
        if total > 0.5:
            sentiment = 'positive'
            score = min(1.0, total / 5.0)
        elif total < -0.5:
            sentiment = 'negative'
            score = max(-1.0, total / 5.0)
        else:
            sentiment = 'neutral'
            score = 0.0
        
        # 计算置信度
        total_matches = len(matched_words['positive']) + len(matched_words['negative'])
        confidence = min(1.0, total_matches / 3.0) if total_matches > 0 else 0.3
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': round(confidence, 3),
            'positive_words': matched_words['positive'][:5],
            'negative_words': matched_words['negative'][:5]
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """批量分析"""
        return [self.analyze_sentiment(text) for text in texts]
    
    def analyze_content_field(self, content: str) -> str:
        """简化的情感分析，直接返回标签"""
        result = self.analyze_sentiment(content)
        return result['sentiment']


# 单例实例
_sentiment_analyzer = None


def get_sentiment_analyzer() -> DeepSentimentAnalyzer:
    """获取情感分析器实例"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = DeepSentimentAnalyzer()
    return _sentiment_analyzer