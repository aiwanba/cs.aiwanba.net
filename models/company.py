from models import db
from datetime import datetime

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    stock_price = db.Column(db.Float, nullable=False, default=10.0)
    total_shares = db.Column(db.Integer, nullable=False, default=1000000)
    industry = db.Column(db.String(50), nullable=False)
    cash = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联关系
    shareholders = db.relationship('Shareholder', backref='company', lazy=True)
    transactions = db.relationship('Transaction', backref='company', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'stock_price': self.stock_price,
            'total_shares': self.total_shares,
            'industry': self.industry,
            'cash': self.cash,
            'created_at': self.created_at.isoformat()
        } 