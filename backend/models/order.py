from extensions import db
from datetime import datetime
from decimal import Decimal

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)  # buy/sell
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/completed/cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='orders')
    company = db.relationship('Company', backref='orders')
    
    def __init__(self, company_id, user_id, order_type, amount, price, status='pending'):
        self.company_id = company_id
        self.user_id = user_id
        self.order_type = order_type
        self.amount = amount
        self.price = Decimal(str(price))
        self.status = status 