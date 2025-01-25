from datetime import datetime
import random
from apps.models.ai import AIPlayer
from apps.models.company import Company
from apps.services.trading_service import TradingService
from app import db

class AIService:
    @staticmethod
    def create_ai_player(name, initial_balance=1000000):
        """创建AI玩家"""
        ai_player = AIPlayer(
            name=name,
            balance=initial_balance,
            risk_preference=random.uniform(0.3, 0.7),  # 风险偏好
            trading_frequency=random.uniform(0.2, 0.8)  # 交易频率
        )
        db.session.add(ai_player)
        db.session.commit()
        return ai_player
    
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
                'volume_signal': 0  # 成交量信号，-1到1之间
            }
            
            # 分析可用股数占比
            volume_ratio = available_shares / company.total_shares
            signal['volume_signal'] = 1 - (2 * volume_ratio)  # 股数越少，信号越强
            
            # 分析价格趋势（这里简化处理，实际应该分析历史数据）
            if price < market_value / company.total_shares:
                signal['price_signal'] = 0.5
            
            # 综合信号
            signal['buy_signal'] = (
                signal['price_signal'] * 0.6 +
                signal['volume_signal'] * 0.4
            )
            
            market_data.append(signal)
        
        return market_data
    
    @staticmethod
    def make_trading_decision(ai_player):
        """AI交易决策"""
        market_data = AIService.analyze_market()
        decisions = []
        
        for signal in market_data:
            # 根据AI的风险偏好调整信号
            adjusted_signal = signal['buy_signal'] * ai_player.risk_preference
            
            # 根据交易频率决定是否执行交易
            if random.random() < ai_player.trading_frequency:
                company = Company.query.get(signal['company_id'])
                
                if adjusted_signal > 0.3:  # 买入信号
                    # 计算购买数量
                    max_shares = min(
                        int(float(ai_player.balance) / float(company.current_price)),
                        company.available_shares
                    )
                    if max_shares > 0:
                        shares = random.randint(1, max_shares)
                        decisions.append({
                            'type': 'buy',
                            'company': company,
                            'shares': shares,
                            'price': float(company.current_price)
                        })
                elif adjusted_signal < -0.3:  # 卖出信号
                    # 检查持仓
                    holding = ai_player.get_holding(company.id)
                    if holding and holding.shares > 0:
                        shares = random.randint(1, holding.shares)
                        decisions.append({
                            'type': 'sell',
                            'company': company,
                            'shares': shares,
                            'price': float(company.current_price)
                        })
        
        return decisions
    
    @staticmethod
    def execute_trades(ai_player):
        """执行AI交易"""
        decisions = AIService.make_trading_decision(ai_player)
        results = []
        
        for decision in decisions:
            if decision['type'] == 'buy':
                success, message = TradingService.buy_stock(
                    ai_player,
                    decision['company'],
                    decision['shares'],
                    decision['price']
                )
            else:  # sell
                success, message = TradingService.sell_stock(
                    ai_player,
                    decision['company'],
                    decision['shares'],
                    decision['price']
                )
            
            results.append({
                'success': success,
                'message': message,
                'decision': decision
            })
        
        return results
    
    @staticmethod
    def run_ai_trading():
        """运行AI交易（定时任务调用）"""
        ai_players = AIPlayer.query.all()
        results = []
        
        for ai_player in ai_players:
            trades = AIService.execute_trades(ai_player)
            results.append({
                'ai_player': ai_player.name,
                'trades': trades
            })
        
        return results 