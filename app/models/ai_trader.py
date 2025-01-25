from app import db
from datetime import datetime
from enum import Enum

class TraderStrategy(Enum):
    CONSERVATIVE = 'conservative'  # 保守策略
    BALANCED = 'balanced'         # 平衡策略
    AGGRESSIVE = 'aggressive'     # 激进策略

class AITrader(db.Model):
    __tablename__ = 'ai_traders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    strategy = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=1000000.0)  # AI交易者初始资金
    profit_rate = db.Column(db.Float, default=0.0)    # 收益率
    trade_count = db.Column(db.Integer, default=0)    # 交易次数
    active = db.Column(db.Boolean, default=True)      # 是否活跃
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    stocks = db.relationship('Stock', backref='ai_trader', lazy=True)
    transactions = db.relationship('Transaction', backref='ai_trader', lazy=True)
    
    def __init__(self, name, strategy):
        self.name = name
        if strategy not in [s.value for s in TraderStrategy]:
            raise ValueError("Invalid trading strategy")
        self.strategy = strategy
    
    def update_balance(self, amount):
        """更新AI交易者余额"""
        self.balance += amount
        if self.balance > 0:
            self.profit_rate = (self.balance - 1000000.0) / 1000000.0 * 100
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'strategy': self.strategy,
            'balance': self.balance,
            'profit_rate': self.profit_rate,
            'trade_count': self.trade_count,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        } 