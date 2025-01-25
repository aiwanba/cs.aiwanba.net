from models import db, AIPlayer, Company, StockHolding, Transaction, NewsEvent
from decimal import Decimal
import random
from datetime import datetime, timedelta

class AITradingService:
    """AI交易服务"""
    
    @staticmethod
    def create_ai_player(name, type='balanced'):
        """创建AI玩家"""
        ai = AIPlayer(name=name, type=type)
        try:
            db.session.add(ai)
            db.session.commit()
            return True, ai
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def analyze_market():
        """分析市场状况"""
        companies = Company.query.all()
        market_data = []
        
        for company in companies:
            # 获取最近10笔交易
            transactions = Transaction.query.filter_by(company_id=company.id)\
                .order_by(Transaction.created_at.desc())\
                .limit(10).all()
            
            if transactions:
                # 计算价格趋势
                prices = [float(tx.price) for tx in transactions]
                avg_price = sum(prices) / len(prices)
                trend = 'up' if prices[0] > avg_price else 'down'
                
                # 计算交易量
                volume = sum(tx.shares for tx in transactions)
                
                market_data.append({
                    'company_id': company.id,
                    'current_price': float(company.current_price),
                    'available_shares': company.available_shares,
                    'trend': trend,
                    'volume': volume,
                    'avg_price': avg_price
                })
        
        return market_data
    
    @staticmethod
    def analyze_market_sentiment():
        """分析市场情绪"""
        # 获取最近24小时的新闻
        yesterday = datetime.now() - timedelta(hours=24)
        news_list = NewsEvent.query.filter(
            NewsEvent.created_at >= yesterday,
            NewsEvent.active == True
        ).all()
        
        # 计算市场情绪得分
        sentiment_score = 0
        news_count = 0
        
        for news in news_list:
            if news.impact_type == 'price' and news.impact_value:
                sentiment_score += news.impact_value
                news_count += 1
        
        if news_count > 0:
            return sentiment_score / news_count
        return 0
    
    @staticmethod
    def analyze_company_trend(company_id):
        """分析公司走势"""
        # 获取最近10笔交易
        transactions = Transaction.query.filter_by(company_id=company_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(10).all()
            
        if not transactions:
            return 0
            
        # 计算价格趋势
        prices = [float(tx.price) for tx in transactions]
        avg_price = sum(prices) / len(prices)
        latest_price = prices[0]
        
        # 计算趋势得分：(最新价格 - 平均价格) / 平均价格
        trend_score = (latest_price - avg_price) / avg_price
        return trend_score
    
    @staticmethod
    def make_trading_decision(ai_player):
        """AI交易决策"""
        # 获取市场情绪
        market_sentiment = AITradingService.analyze_market_sentiment()
        
        # 根据AI类型调整风险系数
        risk_factor = {
            'conservative': 0.5,  # 保守型
            'balanced': 1.0,     # 均衡型
            'aggressive': 2.0    # 激进型
        }.get(ai_player.type, 1.0)
        
        # 获取所有公司
        companies = Company.query.all()
        decisions = []
        
        for company in companies:
            # 分析公司走势
            company_trend = AITradingService.analyze_company_trend(company.id)
            
            # 获取公司相关新闻
            company_news = NewsEvent.query.filter_by(
                company_id=company.id,
                active=True
            ).order_by(NewsEvent.created_at.desc()).first()
            
            # 计算新闻影响
            news_impact = 0
            if company_news and company_news.impact_type == 'price':
                news_impact = company_news.impact_value or 0
            
            # 综合评分
            score = (market_sentiment + company_trend + news_impact) * risk_factor
            
            # 根据评分决定交易行为
            if score > 0.05:  # 看涨
                # 计算购买数量
                available_amount = float(ai_player.balance)
                price = float(company.current_price)
                max_shares = min(
                    int(available_amount / price * 0.1),  # 最多使用10%资金
                    company.available_shares
                )
                
                if max_shares > 0:
                    decisions.append({
                        'action': 'buy',
                        'company_id': company.id,
                        'shares': max_shares,
                        'score': score
                    })
                    
            elif score < -0.05:  # 看跌
                # 查看持仓
                holding = StockHolding.query.filter_by(
                    ai_player_id=ai_player.id,
                    company_id=company.id
                ).first()
                
                if holding and holding.shares > 0:
                    decisions.append({
                        'action': 'sell',
                        'company_id': company.id,
                        'shares': holding.shares,
                        'score': abs(score)
                    })
        
        # 按评分排序，选择最优决策
        decisions.sort(key=lambda x: x['score'], reverse=True)
        return decisions[:3]  # 返回前3个最优决策
    
    @staticmethod
    def execute_trading():
        """执行AI交易（定时运行）"""
        ai_players = AIPlayer.query.filter_by(active=True).all()
        
        for ai in ai_players:
            # 获取交易决策
            decisions = AITradingService.make_trading_decision(ai)
            
            for decision in decisions:
                if decision['action'] == 'buy':
                    AITradingService.buy_stock(
                        ai.id,
                        decision['company_id'],
                        decision['shares']
                    )
                else:
                    AITradingService.sell_stock(
                        ai.id,
                        decision['company_id'],
                        decision['shares']
                    )
    
    @staticmethod
    def execute_buy(ai_id, company_id, shares, price):
        """执行AI买入操作"""
        ai = AIPlayer.query.get(ai_id)
        company = Company.query.get(company_id)
        
        if not all([ai, company]):
            return False, "AI玩家或公司不存在"
        
        total_amount = Decimal(str(price)) * shares
        
        if ai.balance < total_amount:
            return False, "AI余额不足"
        
        if company.available_shares < shares:
            return False, "可用股份不足"
        
        try:
            # 更新公司股份
            company.available_shares -= shares
            company.current_price = Decimal(str(price))
            
            # 更新AI持股
            holding = StockHolding.query.filter_by(
                ai_player_id=ai_id,
                company_id=company_id
            ).first()
            
            if holding:
                holding.shares += shares
            else:
                holding = StockHolding(
                    ai_player_id=ai_id,
                    company_id=company_id,
                    shares=shares
                )
                db.session.add(holding)
            
            # 更新AI余额
            ai.balance -= total_amount
            
            # 记录交易
            transaction = Transaction(
                company_id=company_id,
                seller_id=company.owner_id,
                buyer_id=None,
                ai_buyer_id=ai_id,
                shares=shares,
                price=price,
                total_amount=total_amount
            )
            db.session.add(transaction)
            
            db.session.commit()
            return True, transaction
            
        except Exception as e:
            db.session.rollback()
            return False, str(e) 