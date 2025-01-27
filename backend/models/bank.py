from extensions import db
from datetime import datetime

class Bank(db.Model):
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_assets = db.Column(db.Numeric(20, 2), default=0)
    reserve_ratio = db.Column(db.Float, default=0.1)  # 准备金率
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    owner = db.relationship('User', backref='owned_banks')
    accounts = db.relationship('BankAccount', backref='bank', lazy='dynamic')

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(20, 2), default=0)
    account_type = db.Column(db.String(20), default='savings')  # savings/loan
    interest_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='bank_accounts')

class BankTransaction(db.Model):
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit/withdraw/transfer
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 