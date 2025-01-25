from app import db
from app.models.stock import Transaction
from app.models.company import Company
from app.models.ai_trader import AITrader
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import math

class SentimentService:
    def __init__(self):
        self.sentiment_cache = {}
        self.sentiment_factors = {
            'price_trend': 0.3,      # 价格趋势权重
            'volume_trend': 0.2,     # 交易量趋势权重
            'ai_behavior': 0.2,      # AI行为权重
            'volatility': 0.15,      # 波动率权重
            'market_depth': 0.15     # 市场深度权重
        }
    
    def analyze_market_sentiment(self, company_id=None):
        """分析市场情绪
        返回值范围：-1.0 (极度悲观) 到 1.0 (极度乐观)
        """
        if company_id:
            return self._analyze_company_sentiment(company_id)
        else:
            return self._analyze_overall_sentiment()
    
    def _analyze_company_sentiment(self, company_id):
        """分析单个公司的市场情绪"""
        try:
            # 获取各个因素的情绪值
            price_sentiment = self._analyze_price_trend(company_id)
            volume_sentiment = self._analyze_volume_trend(company_id)
            ai_sentiment = self._analyze_ai_behavior(company_id)
            volatility_sentiment = self._analyze_volatility(company_id)
            depth_sentiment = self._analyze_market_depth(company_id)
            
            # 加权计算总体情绪
            sentiment = (
                price_sentiment * self.sentiment_factors['price_trend'] +
                volume_sentiment * self.sentiment_factors['volume_trend'] +
                ai_sentiment * self.sentiment_factors['ai_behavior'] +
                volatility_sentiment * self.sentiment_factors['volatility'] +
                depth_sentiment * self.sentiment_factors['market_depth']
            )
            
            return round(sentiment, 2)
            
        except Exception as e:
            print(f"Sentiment analysis error: {str(e)}")
            return 0.0
    
    def _analyze_price_trend(self, company_id, periods=[1, 4, 24]):
        """分析价格趋势
        使用多个时间周期的移动平均线
        """
        trends = []
        for hours in periods:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            transactions = Transaction.query.filter(
                Transaction.company_id == company_id,
                Transaction.created_at >= cutoff_time
            ).order_by(Transaction.created_at).all()
            
            if len(transactions) >= 2:
                prices = [t.price for t in transactions]
                ma = np.mean(prices)
                trend = (prices[-1] - ma) / ma
                trends.append(trend)
        
        # 对不同周期的趋势加权平均
        weights = [0.5, 0.3, 0.2]  # 短期更重要
        return np.average(trends, weights=weights) if trends else 0
    
    def _analyze_volume_trend(self, company_id):
        """分析交易量趋势"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # 按小时统计交易量
        hourly_volumes = defaultdict(float)
        transactions = Transaction.query.filter(
            Transaction.company_id == company_id,
            Transaction.created_at >= cutoff_time
        ).all()
        
        for tx in transactions:
            hour = tx.created_at.replace(minute=0, second=0, microsecond=0)
            hourly_volumes[hour] += tx.quantity
        
        if not hourly_volumes:
            return 0
            
        volumes = list(hourly_volumes.values())
        volume_ma = np.mean(volumes)
        
        # 计算最近交易量相对于平均值的变化
        if volumes:
            return (volumes[-1] - volume_ma) / volume_ma if volume_ma > 0 else 0
        return 0
    
    def _analyze_ai_behavior(self, company_id):
        """分析AI交易行为"""
        cutoff_time = datetime.utcnow() - timedelta(hours=4)
        
        # 获取AI交易者的交易
        ai_transactions = Transaction.query.join(AITrader).filter(
            Transaction.company_id == company_id,
            Transaction.created_at >= cutoff_time
        ).all()
        
        if not ai_transactions:
            return 0
        
        # 计算买入/卖出比率
        buys = sum(1 for t in ai_transactions if t.type == 'buy')
        sells = sum(1 for t in ai_transactions if t.type == 'sell')
        
        if buys + sells == 0:
            return 0
            
        return (buys - sells) / (buys + sells)
    
    def _analyze_volatility(self, company_id):
        """分析价格波动率"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        transactions = Transaction.query.filter(
            Transaction.company_id == company_id,
            Transaction.created_at >= cutoff_time
        ).all()
        
        if not transactions:
            return 0
            
        prices = [t.price for t in transactions]
        volatility = np.std(prices) / np.mean(prices) if prices else 0
        
        # 将波动率转换为情绪值（高波动率通常表示负面情绪）
        return -math.tanh(volatility * 2)
    
    def _analyze_market_depth(self, company_id):
        """分析市场深度"""
        company = Company.query.get(company_id)
        if not company:
            return 0
            
        # 计算市场深度（简化版）
        total_shares = company.total_shares
        traded_shares = db.session.query(
            db.func.sum(Transaction.quantity)
        ).filter(
            Transaction.company_id == company_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).scalar() or 0
        
        # 计算24小时换手率
        turnover_rate = traded_shares / total_shares if total_shares > 0 else 0
        
        # 将换手率转换为情绪值
        return math.tanh(turnover_rate * 10)  # 标准化到-1到1之间
    
    def _analyze_overall_sentiment(self):
        """分析整体市场情绪"""
        companies = Company.query.all()
        if not companies:
            return 0
            
        sentiments = []
        for company in companies:
            sentiment = self._analyze_company_sentiment(company.id)
            # 按市值加权
            weight = company.market_cap / sum(c.market_cap for c in companies)
            sentiments.append(sentiment * weight)
        
        return sum(sentiments) 