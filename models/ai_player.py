from datetime import datetime
from . import db

class AIPlayer(db.Model):
    """AI玩家模型"""
    __tablename__ = 'ai_players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 交易风格：保守、激进、均衡
    balance = db.Column(db.Numeric(15, 2), default=1000000.00)  # 初始资金100万
    active = db.Column(db.Boolean, default=True)  # 是否活跃
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    stocks = db.relationship('StockHolding', backref='ai_holder', lazy=True,
                           foreign_keys='StockHolding.ai_player_id') 