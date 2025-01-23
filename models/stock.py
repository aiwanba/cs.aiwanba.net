from app import db
from datetime import datetime

class Stock(db.Model):
    """股票持有模型"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    purchase_price = db.Column(db.Float, nullable=False)  # 购买价格
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow) 