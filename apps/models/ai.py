from datetime import datetime
from app import db

class AIAction(db.Model):
    """AI行为模型"""
    __tablename__ = 'ai_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)  # 'buy', 'sell', 'create_company' 等
    target_id = db.Column(db.Integer)  # 目标ID（公司ID等）
    parameters = db.Column(db.JSON)  # 行为参数
    result = db.Column(db.String(20))  # 行为结果
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def execute(self):
        """执行AI行为"""
        if self.action_type == 'buy':
            # 实现购买逻辑
            pass
        elif self.action_type == 'sell':
            # 实现出售逻辑
            pass 