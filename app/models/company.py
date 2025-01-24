from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_shares = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Float, nullable=False, default=0.0)
    market_cap = db.Column(db.Float, nullable=False, default=0.0)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    stocks = db.relationship('Stock', backref='company', lazy=True)
    transactions = db.relationship('Transaction', backref='company', lazy=True)
    
    def __init__(self, name, symbol, description, total_shares, owner_id):
        self.name = name
        self.symbol = symbol
        self.description = description
        self.total_shares = total_shares
        self.owner_id = owner_id
        self.current_price = 0.0
        self.market_cap = 0.0
    
    def update_market_cap(self):
        """更新公司市值"""
        self.market_cap = self.current_price * self.total_shares
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'description': self.description,
            'total_shares': self.total_shares,
            'current_price': self.current_price,
            'market_cap': self.market_cap,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 