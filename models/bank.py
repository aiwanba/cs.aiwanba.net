from app import db
from datetime import datetime

class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)  # 活期余额
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': self.balance,
            'created_at': self.created_at.isoformat()
        }

class TimeDeposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # 日利率
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='active')  # active, completed

class StockPledgeLoan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    pledged_shares = db.Column(db.Integer, nullable=False)  # 质押股数
    loan_amount = db.Column(db.Float, nullable=False)  # 贷款金额
    interest_rate = db.Column(db.Float, nullable=False, default=0.0002)  # 日利率 0.02%
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False, default='active')  # active, repaid, liquidated 