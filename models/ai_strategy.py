from models import db
from datetime import datetime

class AIStrategy(db.Model):
    """AI交易策略模型"""
    __tablename__ = 'ai_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'conservative', 'aggressive', 'balanced'
    description = db.Column(db.Text)
    risk_tolerance = db.Column(db.Float, nullable=False)  # 0-1之间
    max_position_size = db.Column(db.Float, nullable=False)  # 最大仓位比例
    min_holding_period = db.Column(db.Integer, nullable=False)  # 最小持仓时间（分钟）
    profit_target = db.Column(db.Float, nullable=False)  # 目标收益率
    stop_loss = db.Column(db.Float, nullable=False)  # 止损比例
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AITrader(db.Model):
    """AI交易员模型"""
    __tablename__ = 'ai_traders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('ai_strategies.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    strategy = db.relationship('AIStrategy', backref='traders') 