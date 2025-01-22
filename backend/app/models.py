from datetime import datetime
from . import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=100000.0)  # 账户余额
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

class Stock(db.Model):
    """股票模型"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)  # 股票代码
    name = db.Column(db.String(100), nullable=False)  # 公司名称
    current_price = db.Column(db.Float, nullable=False)  # 当前价格
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Portfolio(db.Model):
    """投资组合模型"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    average_price = db.Column(db.Float, nullable=False)  # 平均购买价格 