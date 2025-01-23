from app import db
from models.ai_strategy import AIStrategy, AITrader
from models.transaction import Transaction
from models.stock import Stock
from models.company import Company
from services.transaction_service import TransactionService
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
import os

class AITradingService:
    """AI交易服务"""
    
    @staticmethod
    def create_ai_trader(user_id, strategy_type, initial_cash):
        """创建AI交易者"""
        # 选择或创建策略
        strategy = AIStrategy.query.filter_by(type=strategy_type).first()
        if not strategy:
            strategy = AITradingService._create_strategy(strategy_type)
            
        # 创建AI交易者
        trader = AITrader(
            user_id=user_id,
            strategy_id=strategy.id,
            current_cash=initial_cash,
            total_value=initial_cash
        )
        
        db.session.add(trader)
        db.session.commit()
        return trader
    
    @staticmethod
    def _create_strategy(strategy_type):
        """创建交易策略"""
        if strategy_type == 'conservative':
            strategy = AIStrategy(
                name='保守策略',
                type='conservative',
                description='低风险、稳定收益的交易策略',
                risk_tolerance=0.3,
                max_position_size=0.2,
                min_holding_period=1440,  # 24小时
                profit_target=0.05,
                stop_loss=0.03
            )
        elif strategy_type == 'aggressive':
            strategy = AIStrategy(
                name='激进策略',
                type='aggressive',
                description='高风险、高收益的交易策略',
                risk_tolerance=0.8,
                max_position_size=0.5,
                min_holding_period=60,  # 1小时
                profit_target=0.15,
                stop_loss=0.1
            )
        else:  # balanced
            strategy = AIStrategy(
                name='平衡策略',
                type='balanced',
                description='中等风险和收益的交易策略',
                risk_tolerance=0.5,
                max_position_size=0.3,
                min_holding_period=720,  # 12小时
                profit_target=0.08,
                stop_loss=0.05
            )
        
        db.session.add(strategy)
        db.session.commit()
        return strategy
    
    @staticmethod
    def analyze_market(stock_id):
        """分析市场状况"""
        # 获取最近24小时的交易数据
        recent_time = datetime.utcnow() - timedelta(hours=24)
        transactions = Transaction.query.filter(
            Transaction.stock_id == stock_id,
            Transaction.status == 'completed',
            Transaction.created_at >= recent_time
        ).order_by(Transaction.created_at.asc()).all()
        
        if not transactions:
            return None
            
        # 转换为DataFrame进行分析
        df = pd.DataFrame([{
            'price': t.price,
            'shares': t.shares,
            'total_amount': t.total_amount,
            'timestamp': t.created_at
        } for t in transactions])
        
        # 计算技术指标
        df['vwap'] = df['total_amount'].cumsum() / df['shares'].cumsum()
        df['price_ma5'] = df['price'].rolling(window=5).mean()
        df['volume_ma5'] = df['shares'].rolling(window=5).mean()
        df['price_std'] = df['price'].rolling(window=5).std()
        
        # 计算市场趋势
        current_price = df['price'].iloc[-1]
        vwap = df['vwap'].iloc[-1]
        price_ma5 = df['price_ma5'].iloc[-1]
        volatility = df['price_std'].iloc[-1] / current_price
        
        return {
            'current_price': current_price,
            'vwap': vwap,
            'price_ma5': price_ma5,
            'volatility': volatility,
            'trend': 'up' if current_price > vwap else 'down',
            'volume_trend': 'up' if df['shares'].iloc[-1] > df['volume_ma5'].iloc[-1] else 'down'
        }
    
    @staticmethod
    def make_trading_decision(trader_id, stock_id):
        """AI交易决策"""
        trader = AITrader.query.get(trader_id)
        if not trader or not trader.is_active:
            return None
            
        # 获取市场分析数据
        market_data = AITradingService.analyze_market(stock_id)
        if not market_data:
            return None
            
        strategy = trader.strategy
        
        # 计算交易信号
        signal = AITradingService._calculate_trading_signal(
            market_data,
            strategy.risk_tolerance
        )
        
        if signal == 0:  # 不交易
            return None
            
        # 确定交易数量
        stock = Stock.query.get(stock_id)
        max_shares = int(trader.current_cash * strategy.max_position_size / market_data['current_price'])
        
        if signal > 0:  # 买入信号
            shares = max_shares
            if shares > 0:
                return {
                    'action': 'buy',
                    'shares': shares,
                    'price': market_data['current_price']
                }
        else:  # 卖出信号
            # 检查持仓
            position = Stock.query.filter_by(
                company_id=trader.user.company_id,
                stock_id=stock_id
            ).first()
            
            if position and position.shares > 0:
                return {
                    'action': 'sell',
                    'shares': position.shares,
                    'price': market_data['current_price']
                }
                
        return None
    
    @staticmethod
    def _calculate_trading_signal(market_data, risk_tolerance):
        """计算交易信号"""
        # 1: 强买入, 0.5: 弱买入, 0: 持观望, -0.5: 弱卖出, -1: 强卖出
        signals = []
        
        # 价格相对VWAP的位置
        price_vwap_ratio = market_data['current_price'] / market_data['vwap']
        if price_vwap_ratio < 0.95:
            signals.append(1 * risk_tolerance)  # 价格显著低于VWAP，买入信号
        elif price_vwap_ratio > 1.05:
            signals.append(-1 * risk_tolerance)  # 价格显著高于VWAP，卖出信号
            
        # 趋势信号
        if market_data['trend'] == 'up' and market_data['volume_trend'] == 'up':
            signals.append(0.5)  # 上涨趋势
        elif market_data['trend'] == 'down' and market_data['volume_trend'] == 'down':
            signals.append(-0.5)  # 下跌趋势
            
        # 波动率信号
        if market_data['volatility'] > 0.1:  # 高波动率
            signals.append(-0.3 * risk_tolerance)  # 降低交易意愿
            
        # 综合信号
        final_signal = np.mean(signals)
        
        # 设置阈值
        if final_signal > 0.3:
            return 1  # 买入
        elif final_signal < -0.3:
            return -1  # 卖出
        return 0  # 观望
    
    @staticmethod
    def execute_ai_trading():
        """执行AI交易"""
        active_traders = AITrader.query.filter_by(is_active=True).all()
        
        for trader in active_traders:
            # 获取所有可交易的股票
            stocks = Stock.query.all()
            
            for stock in stocks:
                # 获取交易决策
                decision = AITradingService.make_trading_decision(trader.id, stock.id)
                
                if decision:
                    try:
                        if decision['action'] == 'buy':
                            TransactionService.create_market_order(
                                company_id=trader.user.company_id,
                                stock_id=stock.id,
                                shares=decision['shares'],
                                is_buy=True
                            )
                        else:  # sell
                            TransactionService.create_market_order(
                                company_id=trader.user.company_id,
                                stock_id=stock.id,
                                shares=decision['shares'],
                                is_buy=False
                            )
                            
                        # 更新交易统计
                        trader.total_trades += 1
                        db.session.commit()
                        
                    except Exception as e:
                        continue  # 交易失败，继续下一个 