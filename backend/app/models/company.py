from . import db, BaseModel
from decimal import Decimal

class Company(BaseModel):
    """公司模型"""
    __tablename__ = 'companies'
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    stock_code = db.Column(db.String(6), unique=True, nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    total_shares = db.Column(db.BigInteger, nullable=False)
    circulating_shares = db.Column(db.BigInteger, nullable=False)
    initial_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    current_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    cash_balance = db.Column(db.DECIMAL(20, 2), nullable=False)
    founder_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1-正常，2-停牌，0-破产
    
    # 关联关系
    shareholdings = db.relationship('Shareholding', backref='company', lazy=True)
    orders = db.relationship('Order', backref='company', lazy=True)
    trades = db.relationship('Trade', backref='company', lazy=True)
    
    def __init__(self, name, stock_code, industry, total_shares, initial_price, founder_id):
        self.name = name
        self.stock_code = stock_code
        self.industry = industry
        self.total_shares = total_shares
        self.circulating_shares = total_shares
        self.initial_price = initial_price
        self.current_price = initial_price
        self.cash_balance = Decimal('0.00')
        self.founder_id = founder_id
    
    def update_price(self, new_price):
        """更新股价"""
        self.current_price = new_price
        db.session.commit()
    
    def get_market_value(self):
        """获取市值"""
        return float(self.current_price * self.total_shares)
    
    def get_top_shareholders(self, limit=10):
        """获取前N大股东"""
        return sorted(self.shareholdings, 
                     key=lambda x: x.shares, 
                     reverse=True)[:limit]
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'stock_code': self.stock_code,
            'industry': self.industry,
            'total_shares': self.total_shares,
            'circulating_shares': self.circulating_shares,
            'initial_price': float(self.initial_price),
            'current_price': float(self.current_price),
            'cash_balance': float(self.cash_balance),
            'founder_id': self.founder_id,
            'status': self.status,
            'market_value': self.get_market_value(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 