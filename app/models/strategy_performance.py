from app import db
from datetime import datetime
from enum import Enum

class PerformanceMetric(Enum):
    RETURN_RATE = 'return_rate'         # 收益率
    SHARPE_RATIO = 'sharpe_ratio'       # 夏普比率
    MAX_DRAWDOWN = 'max_drawdown'       # 最大回撤
    WIN_RATE = 'win_rate'               # 胜率
    PROFIT_FACTOR = 'profit_factor'     # 盈亏比
    VOLATILITY = 'volatility'           # 波动率

class StrategyPerformance(db.Model):
    __tablename__ = 'strategy_performances'
    
    id = db.Column(db.Integer, primary_key=True)
    trader_id = db.Column(db.Integer, db.ForeignKey('ai_traders.id'))
    strategy = db.Column(db.String(50), nullable=False)
    
    # 基础指标
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    total_profit = db.Column(db.Float, default=0.0)
    total_loss = db.Column(db.Float, default=0.0)
    
    # 性能指标
    return_rate = db.Column(db.Float)           # 收益率
    sharpe_ratio = db.Column(db.Float)          # 夏普比率
    max_drawdown = db.Column(db.Float)          # 最大回撤
    win_rate = db.Column(db.Float)              # 胜率
    profit_factor = db.Column(db.Float)         # 盈亏比
    volatility = db.Column(db.Float)            # 波动率
    
    # 时间相关
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trader_id': self.trader_id,
            'strategy': self.strategy,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'return_rate': self.return_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'volatility': self.volatility,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'updated_at': self.updated_at.isoformat()
        } 