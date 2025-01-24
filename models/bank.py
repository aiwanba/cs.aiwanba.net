from app import db
from datetime import datetime
from models.company import Company  # 添加这行，因为有外键关联

class BankAccount(db.Model):
    """银行账户模型"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)  # 账户余额
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    transactions = db.relationship('BankTransaction', backref='account', lazy=True)
    
    def deposit(self, amount):
        """存款操作"""
        self.balance += amount
        self.updated_at = datetime.utcnow()
        
    def withdraw(self, amount):
        """取款操作"""
        if self.balance >= amount:
            self.balance -= amount
            self.updated_at = datetime.utcnow()
            return True
        return False
        
    def transfer(self, target_account, amount):
        """转账操作"""
        if self.withdraw(amount):
            target_account.deposit(amount)
            return True
        return False

class BankTransaction(db.Model):
    """银行交易记录模型"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdraw', 'transfer'
    amount = db.Column(db.Float, nullable=False)
    target_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))  # 转账目标账户
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 