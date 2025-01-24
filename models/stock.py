from models import db
from datetime import datetime

class Stock(db.Model):
    """股票模型"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    current_price = db.Column(db.Float, index=True)  # 添加索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 