from extensions import db
from datetime import datetime

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    holder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # 持股数量
    is_frozen = db.Column(db.Boolean, default=False)  # 是否冻结
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    holder = db.relationship('User', backref='stocks')

class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # 交易数量
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 交易价格
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 