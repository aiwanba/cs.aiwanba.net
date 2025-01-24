from app import db
from datetime import datetime

class Bank(db.Model):
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False, default=0.05)  # 基准利率
    total_deposits = db.Column(db.Float, default=0.0)
    total_loans = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    accounts = db.relationship('BankAccount', backref='bank', lazy=True)
    loans = db.relationship('Loan', backref='bank', lazy=True)
    
    def adjust_interest_rate(self, new_rate):
        """调整利率"""
        self.interest_rate = new_rate
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'interest_rate': self.interest_rate,
            'total_deposits': self.total_deposits,
            'total_loans': self.total_loans,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    interest_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def deposit(self, amount):
        """存款"""
        self.balance += amount
        self.bank.total_deposits += amount
        db.session.commit()
    
    def withdraw(self, amount):
        """取款"""
        if self.balance >= amount:
            self.balance -= amount
            self.bank.total_deposits -= amount
            db.session.commit()
            return True
        return False

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, paid, defaulted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def make_payment(self, amount):
        """还款"""
        if amount <= self.remaining_amount:
            self.remaining_amount -= amount
            if self.remaining_amount == 0:
                self.status = 'paid'
            db.session.commit()
            return True
        return False 