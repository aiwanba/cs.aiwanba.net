from datetime import datetime
from app import db

class BankAccount(db.Model):
    """银行账户模型"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # 'savings' 或 'loan'
    balance = db.Column(db.Numeric(10, 2), nullable=False)  # 账户余额/贷款金额
    interest_rate = db.Column(db.Float, nullable=False)  # 利率
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)  # 贷款到期日
    status = db.Column(db.String(20), default='active')  # 账户状态
    
    def calculate_interest(self):
        """计算利息"""
        if self.account_type == 'savings':
            return float(self.balance) * self.interest_rate / 365
        return 0 