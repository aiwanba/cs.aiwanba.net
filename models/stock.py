from datetime import datetime
from . import db

class StockHolding(db.Model):
    """持股记录"""
    __tablename__ = 'stock_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ai_player_id = db.Column(db.Integer, db.ForeignKey('ai_players.id'))  # 新增AI玩家ID
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Transaction(db.Model):
    """交易记录"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ai_seller_id = db.Column(db.Integer, db.ForeignKey('ai_players.id'))  # 新增AI卖家ID
    ai_buyer_id = db.Column(db.Integer, db.ForeignKey('ai_players.id'))   # 新增AI买家ID
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now) 