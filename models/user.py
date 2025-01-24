from models import db
from datetime import datetime

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ai = db.Column(db.Boolean, default=False)
    ai_strategy = db.Column(db.String(20))  # 'conservative', 'aggressive', 'balanced'
    
    # 关系
    companies = db.relationship('Company', backref='owner', lazy=True)
    stocks = db.relationship('Stock', backref='owner', lazy=True)
    # 移除 transactions 关系，因为 Transaction 模型中没有对应的外键 