from datetime import datetime
from . import db

class StockHolding(db.Model):
    """股票持有记录"""
    __tablename__ = 'stock_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Transaction(db.Model):
    """交易记录"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 交易股数
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 交易价格
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)  # 交易总额
    created_at = db.Column(db.DateTime, default=datetime.now) 