from app import db
from datetime import datetime

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, company_id, owner_id, quantity, purchase_price):
        self.company_id = company_id
        self.owner_id = owner_id
        self.quantity = quantity
        self.purchase_price = purchase_price
    
    def update_quantity(self, amount):
        """更新股票数量"""
        self.quantity += amount
        if self.quantity <= 0:
            db.session.delete(self)
        db.session.commit()
    
    def calculate_value(self):
        """计算当前市值"""
        return self.quantity * self.company.current_price
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'owner_id': self.owner_id,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'current_value': self.calculate_value(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, company_id, user_id, type, quantity, price):
        self.company_id = company_id
        self.user_id = user_id
        self.type = type
        self.quantity = quantity
        self.price = price
        self.total_amount = quantity * price
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'type': self.type,
            'quantity': self.quantity,
            'price': self.price,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat()
        } 