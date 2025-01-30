from . import db, BaseModel
from decimal import Decimal

class Transaction(BaseModel):
    """资金流水模型"""
    __tablename__ = 'transactions'
    
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1-创建公司，2-创建银行，3-存款，4-取款，5-贷款，6-还款
    amount = db.Column(db.DECIMAL(20, 2), nullable=False)  # 金额
    balance = db.Column(db.DECIMAL(20, 2), nullable=False)  # 变动后余额
    related_id = db.Column(db.BigInteger)  # 关联ID
    description = db.Column(db.String(200))  # 说明
    
    # 关联关系
    user = db.relationship('User', backref='transactions', lazy=True)
    
    # 类型常量
    TYPE_CREATE_COMPANY = 1
    TYPE_CREATE_BANK = 2
    TYPE_DEPOSIT = 3
    TYPE_WITHDRAW = 4
    TYPE_LOAN = 5
    TYPE_REPAY = 6 