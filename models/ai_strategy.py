from app import db
from datetime import datetime

class AIStrategy(db.Model):
    """AI交易策略模型"""
    __tablename__ = 'ai_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 策略名称
    type = db.Column(db.String(20), nullable=False)  # conservative, aggressive, balanced
    description = db.Column(db.Text)
    
    # 策略参数
    risk_tolerance = db.Column(db.Float, nullable=False)  # 风险承受度 0-1
    max_position_size = db.Column(db.Float, nullable=False)  # 最大仓位比例
    min_holding_period = db.Column(db.Integer, nullable=False)  # 最小持仓时间(分钟)
    profit_target = db.Column(db.Float, nullable=False)  # 目标收益率
    stop_loss = db.Column(db.Float, nullable=False)  # 止损比例
    
    # 策略性能指标
    total_trades = db.Column(db.Integer, default=0)
    successful_trades = db.Column(db.Integer, default=0)
    total_profit = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ai_traders = db.relationship('AITrader', backref='strategy', lazy=True)

class AITrader(db.Model):
    """AI交易者模型"""
    __tablename__ = 'ai_traders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('ai_strategies.id'), nullable=False)
    
    # 交易状态
    is_active = db.Column(db.Boolean, default=True)
    current_cash = db.Column(db.Float, nullable=False)  # 当前现金
    total_value = db.Column(db.Float, nullable=False)  # 总资产价值
    
    # 性能指标
    total_trades = db.Column(db.Integer, default=0)
    successful_trades = db.Column(db.Integer, default=0)
    total_profit = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 学习参数
    learning_rate = db.Column(db.Float, default=0.01)  # 学习率
    exploration_rate = db.Column(db.Float, default=0.1)  # 探索率 