from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Numeric(10, 2), default=0)  # 现金余额
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_ai = db.Column(db.Boolean, default=False)  # 是否是AI玩家
    
    # 关系
    companies = db.relationship('Company', backref='owner', lazy='dynamic')
    stocks = db.relationship('StockHolding', backref='holder', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    bank_accounts = db.relationship('BankAccount', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_total_assets(self):
        """计算总资产（现金 + 股票市值）"""
        stock_value = sum(holding.current_value() for holding in self.stocks)
        return float(self.balance) + stock_value 