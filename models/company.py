from models import db
from datetime import datetime
from models.user import User

class Company(db.Model):
    """公司模型"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    initial_capital = db.Column(db.Float, nullable=False)
    current_stock_price = db.Column(db.Float, default=0.0)
    total_shares = db.Column(db.Integer, default=10000)  # 默认发行1万股
    
    # 关系
    stocks = db.relationship('Stock', backref='company', lazy=True)
    # 明确指定外键关系
    bought_transactions = db.relationship('Transaction', 
                                        foreign_keys='Transaction.buyer_company_id',
                                        backref='buyer',
                                        lazy=True)
    sold_transactions = db.relationship('Transaction',
                                      foreign_keys='Transaction.seller_company_id',
                                      backref='seller',
                                      lazy=True) 