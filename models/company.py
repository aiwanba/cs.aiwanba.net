from datetime import datetime
from . import db

class Company(db.Model):
    """公司模型"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_shares = db.Column(db.Integer, nullable=False)  # 总股数
    available_shares = db.Column(db.Integer, nullable=False)  # 可交易股数
    current_price = db.Column(db.Numeric(10, 2), nullable=False)  # 当前股价
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_ai = db.Column(db.Boolean, default=False)  # 是否是AI公司
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    stock_holdings = db.relationship('StockHolding', backref='company', lazy=True)
    transactions = db.relationship('Transaction', backref='company', lazy=True) 