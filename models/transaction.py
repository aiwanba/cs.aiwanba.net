from models import db
from datetime import datetime

class Transaction(db.Model):
    """交易记录模型"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    # 交易双方
    seller_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    buyer_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # 交易股票信息
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), index=True)
    shares = db.Column(db.Integer, nullable=False)  # 交易股数
    price = db.Column(db.Float, nullable=False)  # 交易价格
    total_amount = db.Column(db.Float, nullable=False)  # 交易总额
    
    # 交易类型
    order_type = db.Column(db.String(20), nullable=False)  # 'market'(市价单) 或 'limit'(限价单)
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'completed', 'cancelled'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)  # 交易完成时间
    
    # 关系
    stock = db.relationship('Stock', backref='transactions')

class Order(db.Model):
    """订单模型（用于限价单）"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)  # 'buy' 或 'sell'
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 股数
    price = db.Column(db.Float, nullable=False)  # 限价
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    company = db.relationship('Company', backref='orders')
    stock = db.relationship('Stock', backref='orders') 