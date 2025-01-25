from datetime import datetime
from apps.extensions import db

class AIPlayer(db.Model):
    """AI玩家模型"""
    __tablename__ = 'ai_players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    risk_preference = db.Column(db.Float, nullable=False)  # 风险偏好
    trading_frequency = db.Column(db.Float, nullable=False)  # 交易频率
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def execute_action(self, action_type, **params):
        """执行AI行为"""
        if action_type == 'buy':
            # 实现购买逻辑
            pass
        elif action_type == 'sell':
            # 实现出售逻辑
            pass 