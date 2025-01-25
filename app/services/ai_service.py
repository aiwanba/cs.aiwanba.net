from app import db, websocket_service
from app.models.ai_trader import AITrader, TraderStrategy
from app.models.company import Company
from app.models.stock import Stock, Transaction
from app.utils.exceptions import StockError
from flask_socketio import emit
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import random

class AIService:
    def __init__(self):
        self.active = False
        self.trading_thread = None
    
    def start_trading(self):
        """启动AI交易"""
        if not self.active:
            self.active = True
            self.trading_thread = threading.Thread(target=self._trading_loop)
            self.trading_thread.daemon = True
            self.trading_thread.start()
    
    def stop_trading(self):
        """停止AI交易"""
        self.active = False
        if self.trading_thread:
            self.trading_thread.join()
    
    def _trading_loop(self):
        """AI交易主循环"""
        while self.active:
            try:
                # 获取所有活跃的AI交易者
                traders = AITrader.query.filter_by(active=True).all()
                
                for trader in traders:
                    # 根据不同策略进行交易
                    if trader.strategy == TraderStrategy.CONSERVATIVE.value:
                        self._conservative_strategy(trader)
                    elif trader.strategy == TraderStrategy.BALANCED.value:
                        self._balanced_strategy(trader)
                    elif trader.strategy == TraderStrategy.AGGRESSIVE.value:
                        self._aggressive_strategy(trader)
                    elif trader.strategy == TraderStrategy.MOMENTUM.value:
                        self._momentum_strategy(trader)
                    elif trader.strategy == TraderStrategy.MEAN_REVERSION.value:
                        self._mean_reversion_strategy(trader)
                
                # 休眠一段时间
                time.sleep(random.uniform(5, 15))  # 随机5-15秒
                
            except Exception as e:
                print(f"AI trading error: {str(e)}")
                time.sleep(5)  # 发生错误时暂停5秒
    
    def _conservative_strategy(self, trader):
        """保守策略：
        - 主要投资市值较大、波动较小的公司
        - 持有时间较长
        - 单次交易金额较小
        """
        try:
            # 获取市值排名前30%的公司
            companies = Company.query.order_by(Company.market_cap.desc()).limit(10).all()
            
            for company in companies:
                # 计算过去24小时的价格波动
                volatility = self._calculate_volatility(company)
                
                if volatility < 0.05:  # 波动率小于5%
                    # 随机决定买入或卖出
                    if random.random() < 0.6:  # 60%概率买入
                        self._execute_trade(trader, company, 'buy', 
                                         max_amount=trader.balance * 0.05)
                    else:
                        self._execute_trade(trader, company, 'sell', 
                                         max_amount=trader.balance * 0.03)
        
        except Exception as e:
            print(f"Conservative strategy error: {str(e)}")
    
    def _balanced_strategy(self, trader):
        """平衡策略：
        - 综合考虑公司市值和价格趋势
        - 中等持有时间
        - 适中的交易金额
        """
        try:
            # 获取所有活跃交易的公司
            companies = Company.query.all()
            
            for company in companies:
                # 分析价格趋势
                trend = self._analyze_trend(company)
                
                if trend > 0:  # 上升趋势
                    self._execute_trade(trader, company, 'buy', 
                                     max_amount=trader.balance * 0.1)
                elif trend < 0:  # 下降趋势
                    self._execute_trade(trader, company, 'sell', 
                                     max_amount=trader.balance * 0.08)
        
        except Exception as e:
            print(f"Balanced strategy error: {str(e)}")
    
    def _aggressive_strategy(self, trader):
        """激进策略：
        - 追求高收益，接受高风险
        - 短期持有
        - 大额交易
        """
        try:
            # 获取24小时内价格变化最大的公司
            companies = Company.query.all()
            volatilities = [(c, self._calculate_volatility(c)) for c in companies]
            volatile_companies = sorted(volatilities, key=lambda x: x[1], reverse=True)[:5]
            
            for company, volatility in volatile_companies:
                if volatility > 0.1:  # 波动率大于10%
                    # 根据短期趋势决定买入或卖出
                    trend = self._analyze_trend(company, period='short')
                    
                    if trend > 0:
                        self._execute_trade(trader, company, 'buy', 
                                         max_amount=trader.balance * 0.2)
                    else:
                        self._execute_trade(trader, company, 'sell', 
                                         max_amount=trader.balance * 0.15)
        
        except Exception as e:
            print(f"Aggressive strategy error: {str(e)}")
    
    def _momentum_strategy(self, trader):
        """动量策略：
        - 追踪价格动量
        - 突破点买入
        - 止损点卖出
        """
        try:
            from app.services.sentiment_service import SentimentService
            sentiment_service = SentimentService()
            
            companies = Company.query.all()
            for company in companies:
                # 计算动量指标
                momentum = self._calculate_momentum(company)
                sentiment = sentiment_service.analyze_market_sentiment(company.id)
                
                # 结合动量和情绪做决策
                signal = momentum * 0.7 + sentiment * 0.3
                
                if signal > 0.5:  # 强烈买入信号
                    self._execute_trade(trader, company, 'buy', 
                                     max_amount=trader.balance * 0.15)
                elif signal < -0.5:  # 强烈卖出信号
                    self._execute_trade(trader, company, 'sell', 
                                     max_amount=trader.balance * 0.15)
                    
        except Exception as e:
            print(f"Momentum strategy error: {str(e)}")
    
    def _mean_reversion_strategy(self, trader):
        """均值回归策略：
        - 寻找偏离均值的价格
        - 预期价格会回归均值
        """
        try:
            companies = Company.query.all()
            for company in companies:
                # 计算价格相对于均值的偏离度
                deviation = self._calculate_price_deviation(company)
                
                if deviation > 0.1:  # 价格显著高于均值
                    self._execute_trade(trader, company, 'sell', 
                                     max_amount=trader.balance * 0.1)
                elif deviation < -0.1:  # 价格显著低于均值
                    self._execute_trade(trader, company, 'buy', 
                                     max_amount=trader.balance * 0.1)
                    
        except Exception as e:
            print(f"Mean reversion strategy error: {str(e)}")
    
    def _calculate_volatility(self, company, period=24):
        """计算价格波动率"""
        # 获取过去24小时的交易记录
        cutoff_time = datetime.utcnow() - timedelta(hours=period)
        transactions = Transaction.query.filter(
            Transaction.company_id == company.id,
            Transaction.created_at >= cutoff_time
        ).all()
        
        if not transactions:
            return 0
            
        prices = [t.price for t in transactions]
        return np.std(prices) / np.mean(prices) if prices else 0
    
    def _analyze_trend(self, company, period='medium'):
        """分析价格趋势"""
        if period == 'short':
            hours = 4
        elif period == 'medium':
            hours = 24
        else:
            hours = 72
            
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        transactions = Transaction.query.filter(
            Transaction.company_id == company.id,
            Transaction.created_at >= cutoff_time
        ).order_by(Transaction.created_at).all()
        
        if len(transactions) < 2:
            return 0
            
        # 简单线性回归
        prices = [t.price for t in transactions]
        times = [(t.created_at - cutoff_time).total_seconds() for t in transactions]
        
        if len(prices) < 2:
            return 0
            
        slope = np.polyfit(times, prices, 1)[0]
        return slope 
    
    def _calculate_momentum(self, company, periods=[5, 15, 30]):
        """计算价格动量"""
        momentum_values = []
        
        for minutes in periods:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            transactions = Transaction.query.filter(
                Transaction.company_id == company.id,
                Transaction.created_at >= cutoff_time
            ).order_by(Transaction.created_at).all()
            
            if len(transactions) >= 2:
                prices = [t.price for t in transactions]
                momentum = (prices[-1] - prices[0]) / prices[0]
                momentum_values.append(momentum)
        
        return np.mean(momentum_values) if momentum_values else 0
    
    def _calculate_price_deviation(self, company):
        """计算价格偏离度"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        transactions = Transaction.query.filter(
            Transaction.company_id == company.id,
            Transaction.created_at >= cutoff_time
        ).all()
        
        if not transactions:
            return 0
            
        prices = [t.price for t in transactions]
        mean_price = np.mean(prices)
        
        return (company.current_price - mean_price) / mean_price if mean_price > 0 else 0
    
    def _execute_trade(self, trader, company, trade_type, max_amount):
        """执行交易"""
        try:
            if trade_type == 'buy':
                # 计算可买入的最大股数
                max_shares = int(max_amount / company.current_price)
                if max_shares > 0:
                    # 随机决定实际买入数量
                    shares = random.randint(1, max_shares)
                    total_cost = shares * company.current_price
                    
                    if trader.balance >= total_cost:
                        # 创建交易记录
                        transaction = Transaction(
                            company_id=company.id,
                            user_id=trader.id,
                            type='buy',
                            quantity=shares,
                            price=company.current_price
                        )
                        
                        # 更新AI交易者余额和持仓
                        trader.update_balance(-total_cost)
                        trader.trade_count += 1
                        
                        # 更新或创建持仓记录
                        stock = Stock.query.filter_by(
                            company_id=company.id,
                            owner_id=trader.id
                        ).first()
                        
                        if stock:
                            stock.update_quantity(shares)
                        else:
                            stock = Stock(
                                company_id=company.id,
                                owner_id=trader.id,
                                quantity=shares,
                                purchase_price=company.current_price
                            )
                            db.session.add(stock)
                        
                        db.session.add(transaction)
                        db.session.commit()
                        
                        # 使用WebSocket服务广播交易
                        websocket_service.broadcast_transaction({
                            'trader_id': trader.id,
                            'trader_name': trader.name,
                            'type': 'buy',
                            'company_id': company.id,
                            'quantity': shares,
                            'price': company.current_price,
                            'total': total_cost,
                            'trader_type': 'ai'
                        })
            
            elif trade_type == 'sell':
                # 获取当前持仓
                stock = Stock.query.filter_by(
                    company_id=company.id,
                    owner_id=trader.id
                ).first()
                
                if stock and stock.quantity > 0:
                    # 随机决定卖出数量
                    max_shares = min(stock.quantity, int(max_amount / company.current_price))
                    shares = random.randint(1, max_shares)
                    total_income = shares * company.current_price
                    
                    # 创建交易记录
                    transaction = Transaction(
                        company_id=company.id,
                        user_id=trader.id,
                        type='sell',
                        quantity=shares,
                        price=company.current_price
                    )
                    
                    # 更新AI交易者余额和持仓
                    trader.update_balance(total_income)
                    trader.trade_count += 1
                    stock.update_quantity(-shares)
                    
                    db.session.add(transaction)
                    db.session.commit()
                    
                    # 使用WebSocket服务广播交易
                    websocket_service.broadcast_transaction({
                        'trader_id': trader.id,
                        'trader_name': trader.name,
                        'type': 'sell',
                        'company_id': company.id,
                        'quantity': shares,
                        'price': company.current_price,
                        'total': total_income,
                        'trader_type': 'ai'
                    })
        
        except Exception as e:
            db.session.rollback()
            print(f"Trade execution error: {str(e)}") 