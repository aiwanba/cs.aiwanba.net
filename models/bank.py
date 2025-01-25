from datetime import datetime
from . import db
from decimal import Decimal

class BankAccount(db.Model):
    """银行账户"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0)  # 存款余额
    interest_rate = db.Column(db.Numeric(5, 2), default=3.00)  # 年利率，默认3%
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BankLoan(db.Model):
    """银行贷款"""
    __tablename__ = 'bank_loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # 贷款金额
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)  # 年利率
    term_months = db.Column(db.Integer, nullable=False)  # 贷款期限（月）
    remaining_amount = db.Column(db.Numeric(15, 2), nullable=False)  # 剩余待还
    status = db.Column(db.String(20), default='active')  # active, paid, overdue
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BankTransaction(db.Model):
    """银行交易记录"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # deposit, withdraw, interest, loan, repayment
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance_after = db.Column(db.Numeric(15, 2), nullable=False)  # 交易后余额
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now) 