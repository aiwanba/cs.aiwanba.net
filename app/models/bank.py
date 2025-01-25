from app import db
from datetime import datetime, timedelta
from enum import Enum

class AccountType(Enum):
    SAVINGS = 'savings'       # 储蓄账户
    CHECKING = 'checking'     # 支票账户
    MARGIN = 'margin'         # 保证金账户
    BUSINESS = 'business'     # 企业账户

class LoanStatus(Enum):
    PENDING = 'pending'       # 待审核
    APPROVED = 'approved'     # 已批准
    ACTIVE = 'active'         # 进行中
    OVERDUE = 'overdue'      # 逾期
    COMPLETED = 'completed'   # 已完成
    REJECTED = 'rejected'     # 已拒绝

class Bank(db.Model):
    __tablename__ = 'banks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    reserve_ratio = db.Column(db.Float, default=0.1)  # 准备金率
    base_interest_rate = db.Column(db.Float, default=0.05)  # 基准利率
    loan_interest_rate = db.Column(db.Float, default=0.08)  # 贷款利率
    total_deposits = db.Column(db.Float, default=0.0)
    total_loans = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    accounts = db.relationship('BankAccount', backref='bank', lazy=True)
    loans = db.relationship('Loan', backref='bank', lazy=True)

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    interest_rate = db.Column(db.Float)  # 账户利率
    credit_limit = db.Column(db.Float, default=0.0)  # 信用额度
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, bank_id, account_type):
        if account_type not in [t.value for t in AccountType]:
            raise ValueError("Invalid account type")
            
        self.user_id = user_id
        self.bank_id = bank_id
        self.account_type = account_type
        self.account_number = self._generate_account_number()
        self.interest_rate = self._get_initial_interest_rate()
    
    def _generate_account_number(self):
        """生成账号"""
        import random
        return f"{self.bank_id:02d}{datetime.utcnow().strftime('%Y%m')}{random.randint(1000, 9999)}"
    
    def _get_initial_interest_rate(self):
        """获取初始利率"""
        bank = Bank.query.get(self.bank_id)
        if self.account_type == AccountType.SAVINGS.value:
            return bank.base_interest_rate
        elif self.account_type == AccountType.MARGIN.value:
            return bank.loan_interest_rate
        return 0.0

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)  # 贷款期限（月）
    monthly_payment = db.Column(db.Float)  # 月供
    remaining_amount = db.Column(db.Float)  # 剩余金额
    status = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.Text)  # 贷款用途
    collateral = db.Column(db.Text)  # 抵押物
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    
    def __init__(self, user_id, bank_id, amount, term_months, purpose=None, collateral=None):
        self.user_id = user_id
        self.bank_id = bank_id
        self.amount = amount
        self.term_months = term_months
        self.purpose = purpose
        self.collateral = collateral
        self.status = LoanStatus.PENDING.value
        
        # 获取银行贷款利率
        bank = Bank.query.get(bank_id)
        self.interest_rate = bank.loan_interest_rate
        
        # 计算月供
        self._calculate_monthly_payment()
        self.remaining_amount = amount
    
    def _calculate_monthly_payment(self):
        """计算月供（等额本息）"""
        monthly_rate = self.interest_rate / 12
        self.monthly_payment = (
            self.amount * 
            monthly_rate * (1 + monthly_rate) ** self.term_months
        ) / ((1 + monthly_rate) ** self.term_months - 1)
    
    def approve(self):
        """批准贷款"""
        self.status = LoanStatus.APPROVED.value
        self.approved_at = datetime.utcnow()
        self.next_payment_date = datetime.utcnow().replace(
            day=1
        ) + timedelta(days=32)  # 下个月1号
        
    def make_payment(self, amount):
        """还款"""
        if amount >= self.monthly_payment:
            self.remaining_amount -= (amount - self.monthly_payment * self.interest_rate)
            if self.remaining_amount <= 0:
                self.status = LoanStatus.COMPLETED.value
            else:
                self.next_payment_date = self.next_payment_date + timedelta(days=30)
            return True
        return False 