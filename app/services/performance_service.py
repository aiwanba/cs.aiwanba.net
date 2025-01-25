from app import db
from app.models.strategy_performance import StrategyPerformance
from app.models.ai_trader import AITrader
from app.models.stock import Transaction
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

class PerformanceService:
    def __init__(self):
        self.risk_free_rate = 0.02  # 年化无风险利率
        
    def evaluate_strategy(self, trader_id, period_days=30):
        """评估交易策略性能"""
        try:
            trader = AITrader.query.get(trader_id)
            if not trader:
                raise ValueError("Trader not found")
                
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # 获取交易记录
            transactions = Transaction.query.filter(
                Transaction.user_id == trader_id,
                Transaction.created_at.between(start_date, end_date)
            ).order_by(Transaction.created_at).all()
            
            if not transactions:
                return None
                
            # 计算各项指标
            performance = self._calculate_performance_metrics(
                trader=trader,
                transactions=transactions,
                start_date=start_date,
                end_date=end_date
            )
            
            # 保存或更新性能记录
            self._save_performance(performance)
            
            return performance
            
        except Exception as e:
            print(f"Strategy evaluation error: {str(e)}")
            return None
    
    def _calculate_performance_metrics(self, trader, transactions, start_date, end_date):
        """计算性能指标"""
        # 基础统计
        total_trades = len(transactions)
        profits = []
        daily_returns = defaultdict(float)
        
        # 计算每笔交易的盈亏
        for tx in transactions:
            profit = self._calculate_trade_profit(tx)
            profits.append(profit)
            
            # 记录每日收益
            date = tx.created_at.date()
            daily_returns[date] += profit
        
        # 计算胜率
        winning_trades = sum(1 for p in profits if p > 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 计算总盈亏
        total_profit = sum(p for p in profits if p > 0)
        total_loss = abs(sum(p for p in profits if p < 0))
        
        # 计算收益率
        initial_balance = 1000000  # AI交易者初始资金
        return_rate = (trader.balance - initial_balance) / initial_balance
        
        # 计算夏普比率
        daily_return_values = list(daily_returns.values())
        if daily_return_values:
            avg_daily_return = np.mean(daily_return_values)
            daily_volatility = np.std(daily_return_values)
            sharpe_ratio = self._calculate_sharpe_ratio(
                avg_daily_return, daily_volatility
            )
        else:
            sharpe_ratio = 0
        
        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(daily_returns)
        
        # 创建性能记录
        performance = StrategyPerformance(
            trader_id=trader.id,
            strategy=trader.strategy,
            total_trades=total_trades,
            winning_trades=winning_trades,
            total_profit=total_profit,
            total_loss=total_loss,
            return_rate=return_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=total_profit / total_loss if total_loss > 0 else float('inf'),
            volatility=daily_volatility if 'daily_volatility' in locals() else 0,
            start_date=start_date,
            end_date=end_date
        )
        
        return performance
    
    def _calculate_trade_profit(self, transaction):
        """计算单笔交易盈亏"""
        if transaction.type == 'buy':
            return -transaction.quantity * transaction.price
        else:  # sell
            return transaction.quantity * transaction.price
    
    def _calculate_sharpe_ratio(self, avg_daily_return, daily_volatility):
        """计算夏普比率"""
        if daily_volatility == 0:
            return 0
            
        # 年化
        annual_return = (1 + avg_daily_return) ** 252 - 1
        annual_volatility = daily_volatility * np.sqrt(252)
        
        return (annual_return - self.risk_free_rate) / annual_volatility
    
    def _calculate_max_drawdown(self, daily_returns):
        """计算最大回撤"""
        cumulative_returns = []
        current_cum = 0
        
        for date in sorted(daily_returns.keys()):
            current_cum += daily_returns[date]
            cumulative_returns.append(current_cum)
        
        if not cumulative_returns:
            return 0
            
        peak = cumulative_returns[0]
        max_drawdown = 0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _save_performance(self, performance):
        """保存性能记录"""
        try:
            # 检查是否存在最近的记录
            existing = StrategyPerformance.query.filter_by(
                trader_id=performance.trader_id
            ).order_by(
                StrategyPerformance.end_date.desc()
            ).first()
            
            if existing and existing.end_date >= performance.start_date:
                # 更新现有记录
                for key, value in performance.to_dict().items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # 创建新记录
                db.session.add(performance)
                
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Performance save error: {str(e)}") 