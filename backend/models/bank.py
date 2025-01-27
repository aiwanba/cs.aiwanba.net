from extensions import db
from datetime import datetime
from decimal import Decimal

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
    accounts = db.relationship('BankAccount', backref='bank')

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Numeric(20, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, account_number, bank_id):
        self.user_id = user_id
        self.bank_id = bank_id
        self.account_number = account_number
        self.balance = Decimal('0')

class BankTransaction(db.Model):
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit/withdraw/transfer
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 