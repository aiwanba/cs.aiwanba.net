from models import db, AIPlayer, Company, StockHolding, Transaction
from decimal import Decimal
import random

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
    def make_trading_decision(ai_player):
        """AI做出交易决策"""
        market_data = AITradingService.analyze_market()
        decisions = []
        
        for data in market_data:
            if ai_player.type == 'conservative':
                # 保守型AI：只在价格低于平均价格时买入
                if data['current_price'] < data['avg_price'] * 0.95:
                    decisions.append({
                        'action': 'buy',
                        'company_id': data['company_id'],
                        'shares': min(100, data['available_shares']),
                        'price': data['current_price']
                    })
            elif ai_player.type == 'aggressive':
                # 激进型AI：在价格上涨趋势时买入
                if data['trend'] == 'up':
                    decisions.append({
                        'action': 'buy',
                        'company_id': data['company_id'],
                        'shares': min(500, data['available_shares']),
                        'price': data['current_price'] * 1.02
                    })
            else:  # balanced
                # 均衡型AI：根据趋势和价格综合决策
                if data['trend'] == 'up' and data['current_price'] < data['avg_price']:
                    decisions.append({
                        'action': 'buy',
                        'company_id': data['company_id'],
                        'shares': min(200, data['available_shares']),
                        'price': data['current_price']
                    })
        
        return decisions
    
    @staticmethod
    def execute_trades():
        """执行AI交易"""
        ai_players = AIPlayer.query.filter_by(active=True).all()
        trades_executed = []
        
        for ai in ai_players:
            decisions = AITradingService.make_trading_decision(ai)
            for decision in decisions:
                if decision['action'] == 'buy':
                    success, result = AITradingService.execute_buy(
                        ai.id,
                        decision['company_id'],
                        decision['shares'],
                        decision['price']
                    )
                    if success:
                        trades_executed.append(result)
        
        return trades_executed
    
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