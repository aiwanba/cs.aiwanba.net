from datetime import datetime
from . import db  # 改用__init__.py中的db实例

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=100000.00)  # 初始资金10万
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    companies = db.relationship('Company', backref='owner', lazy=True)
    stocks = db.relationship('StockHolding', backref='holder', lazy=True) 