from models import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    buyer_id = db.Column(db.Integer, nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 交易股数
    price = db.Column(db.Float, nullable=False)  # 成交价格
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'seller_id': self.seller_id,
            'buyer_id': self.buyer_id,
            'shares': self.shares,
            'price': self.price,
            'total_amount': self.shares * self.price,
            'created_at': self.created_at.isoformat()
        }

class OrderBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    order_type = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    shares = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False, default='pending')  # pending, completed, cancelled 