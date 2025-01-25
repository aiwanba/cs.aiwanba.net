from datetime import datetime
import random
from apps.models.ai import AIPlayer
from apps.models.company import Company
from apps.services.trading_service import TradingService
from apps.extensions import db

class AIService:
    @staticmethod
    def create_ai_player(name, balance=10000.0, risk_preference=0.5):
        """创建AI玩家"""
        ai = AIPlayer(
            name=name,
            balance=balance,
            risk_preference=risk_preference,
            trading_frequency=random.uniform(0.3, 0.8)
        )
        
        db.session.add(ai)
        db.session.commit()
        
        return ai
    
    @staticmethod
    def make_decisions():
        """AI玩家决策"""
        ai_players = AIPlayer.query.all()
        companies = Company.query.all()
        results = []
        
        for ai in ai_players:
            # 根据风险偏好和交易频率决定是否交易
            if random.random() > ai.trading_frequency:
                continue
                
            for company in companies:
                decision = random.choice(['buy', 'sell', 'hold'])
                success = False
                message = ""
                
                if decision == 'buy':
                    # 计算购买数量和价格
                    max_shares = int(float(ai.balance) / float(company.current_price))
                    if max_shares > 0:
                        shares = random.randint(1, min(max_shares, 100))
                        success, result = TradingService.buy_stock(
                            ai,
                            company,
                            shares,
                            float(company.current_price)
                        )
                        message = "购买成功" if success else result
                
                elif decision == 'sell':
                    # 查找持仓并卖出
                    holding = next(
                        (h for h in ai.stocks if h.company_id == company.id),
                        None
                    )
                    if holding:
                        shares = random.randint(1, holding.shares)
                        success, result = TradingService.sell_stock(
                            ai,
                            company,
                            shares,
                            float(company.current_price)
                        )
                        message = "出售成功" if success else result
                
                results.append({
                    'ai_name': ai.name,
                    'company_name': company.name,
                    'action': decision,
                    'success': success,
                    'message': message
                })
        
        return results

    @staticmethod
    def analyze_market():
        """分析市场状况"""
        companies = Company.query.all()
        market_data = []
        
        for company in companies:
            # 计算基本面指标
            market_value = company.market_value()
            available_shares = company.available_shares
            price = float(company.current_price)
            
            # 计算交易信号
            signal = {
                'company_id': company.id,
                'buy_signal': 0,  # -1到1之间，大于0表示买入信号
                'price_signal': 0,  # 价格合理性，-1到1之间
            }
            market_data.append(signal)
        
        return market_data
    
    @staticmethod
    def run_ai_trading():
        """运行AI交易（定时任务调用）"""
        ai_players = AIPlayer.query.all()
        results = []
        
        for ai_player in ai_players:
            # 分析市场
            market_data = AIService.analyze_market()
            
            # 生成交易决策
            decisions = []
            for signal in market_data:
                if signal['buy_signal'] > 0.5:  # 买入阈值
                    decisions.append({
                        'type': 'buy',
                        'company_id': signal['company_id'],
                        'shares': 100,  # 示例固定数量
                        'price': Company.query.get(signal['company_id']).current_price
                    })
            
            # 执行交易
            for decision in decisions:
                company = Company.query.get(decision['company_id'])
                if decision['type'] == 'buy':
                    success, message = TradingService.buy_stock(
                        ai_player,
                        company,
                        decision['shares'],
                        float(decision['price'])
                    )
                else:  # sell
                    success, message = TradingService.sell_stock(
                        ai_player,
                        company,
                        decision['shares'],
                        float(decision['price'])
                    )
                
                results.append({
                    'ai_player': ai_player.name,
                    'action': decision,
                    'success': success,
                    'message': message
                })
        
        return results 