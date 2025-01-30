from . import db, BaseModel
import bcrypt

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cash = db.Column(db.DECIMAL(20, 2), default=10000000.00)
    is_admin = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)  # 1-正常，0-禁用
    
    # 关联关系
    companies = db.relationship('Company', backref='founder', lazy=True)
    shareholdings = db.relationship('Shareholding', backref='shareholder', lazy=True)
    banks = db.relationship('Bank', backref='owner', lazy=True)
    deposits = db.relationship('Deposit', backref='depositor', lazy=True)
    loans = db.relationship('Loan', backref='borrower', lazy=True)
    orders = db.relationship('Order', backref='trader', lazy=True)
    received_messages = db.relationship('MessageRecipient', backref='recipient', lazy=True)
    
    def __init__(self, username, password, email):
        self.username = username
        self.set_password(password)
        self.email = email
    
    def set_password(self, password):
        """设置密码"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def get_holdings(self):
        """获取用户的所有持股"""
        return {holding.company_id: holding.shares for holding in self.shareholdings}
    
    def update_cash(self, amount):
        """更新用户现金余额"""
        self.cash += amount
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'cash': float(self.cash),
            'is_admin': self.is_admin,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 