from datetime import datetime
from apps.extensions import db

class Transaction(db.Model):
    """交易记录模型"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'buy' 或 'sell'
    shares = db.Column(db.Integer, nullable=False)  # 交易股数
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 交易价格
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)  # 交易总额
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_total(self):
        """计算交易总额"""
        return float(self.price) * self.shares 