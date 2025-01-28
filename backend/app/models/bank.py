from . import db, BaseModel
from decimal import Decimal

class Bank(BaseModel):
    """银行模型"""
    __tablename__ = 'banks'
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    capital = db.Column(db.DECIMAL(20, 2), nullable=False)  # 注册资本
    reserve_ratio = db.Column(db.DECIMAL(5, 2), default=10.00)  # 准备金率
    deposit_rate = db.Column(db.DECIMAL(5, 2), nullable=False)  # 存款利率
    loan_rate = db.Column(db.DECIMAL(5, 2), nullable=False)  # 贷款利率
    total_deposit = db.Column(db.DECIMAL(20, 2), default=0)  # 存款总额
    total_loan = db.Column(db.DECIMAL(20, 2), default=0)  # 贷款总额
    status = db.Column(db.Integer, default=1)  # 1-正常，0-破产
    
    # 关联关系
    deposits = db.relationship('Deposit', backref='bank', lazy=True)
    loans = db.relationship('Loan', backref='bank', lazy=True)
    
    def __init__(self, name, owner_id, capital, deposit_rate, loan_rate):
        self.name = name
        self.owner_id = owner_id
        self.capital = capital
        self.deposit_rate = deposit_rate
        self.loan_rate = loan_rate
    
    def get_available_funds(self):
        """获取可贷资金"""
        required_reserve = self.total_deposit * (self.reserve_ratio / 100)
        return float(self.capital + self.total_deposit - required_reserve - self.total_loan)
    
    def can_loan(self, amount):
        """检查是否可以发放贷款"""
        return self.get_available_funds() >= float(amount)
    
    def update_deposit_rate(self, new_rate):
        """更新存款利率"""
        self.deposit_rate = new_rate
        db.session.commit()
    
    def update_loan_rate(self, new_rate):
        """更新贷款利率"""
        self.loan_rate = new_rate
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id,
            'capital': float(self.capital),
            'reserve_ratio': float(self.reserve_ratio),
            'deposit_rate': float(self.deposit_rate),
            'loan_rate': float(self.loan_rate),
            'total_deposit': float(self.total_deposit),
            'total_loan': float(self.total_loan),
            'available_funds': self.get_available_funds(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Deposit(BaseModel):
    """存款模型"""
    __tablename__ = 'deposits'
    
    bank_id = db.Column(db.BigInteger, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.DECIMAL(20, 2), nullable=False)
    interest_rate = db.Column(db.DECIMAL(5, 2), nullable=False)
    term = db.Column(db.Integer, nullable=False)  # 期限(天)
    start_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1-正常，2-已支取，0-违约
    
    def calculate_interest(self, current_date):
        """计算利息"""
        if current_date > self.end_date:
            days = (self.end_date - self.start_date).days
        else:
            days = (current_date - self.start_date).days
        return float(self.amount * (self.interest_rate / 100) * (days / 365))
    
    def withdraw(self):
        """支取存款"""
        if self.status != 1:
            return False
        self.status = 2
        db.session.commit()
        return True
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'bank_id': self.bank_id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'interest_rate': float(self.interest_rate),
            'term': self.term,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Loan(BaseModel):
    """贷款模型"""
    __tablename__ = 'loans'
    
    bank_id = db.Column(db.BigInteger, db.ForeignKey('banks.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.DECIMAL(20, 2), nullable=False)
    interest_rate = db.Column(db.DECIMAL(5, 2), nullable=False)
    term = db.Column(db.Integer, nullable=False)  # 期限(天)
    start_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=False)
    collateral_type = db.Column(db.Integer)  # 1-股票，2-存单
    collateral_id = db.Column(db.BigInteger)
    status = db.Column(db.Integer, default=1)  # 1-正常，2-已还清，0-违约
    
    def calculate_interest(self, current_date):
        """计算利息"""
        if current_date > self.end_date:
            days = (self.end_date - self.start_date).days
        else:
            days = (current_date - self.start_date).days
        return float(self.amount * (self.interest_rate / 100) * (days / 365))
    
    def repay(self):
        """还款"""
        if self.status != 1:
            return False
        self.status = 2
        db.session.commit()
        return True
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'bank_id': self.bank_id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'interest_rate': float(self.interest_rate),
            'term': self.term,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'collateral_type': self.collateral_type,
            'collateral_id': self.collateral_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        } 