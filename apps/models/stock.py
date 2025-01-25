from datetime import datetime
from app import db

class StockHolding(db.Model):
    """股票持有记录模型"""
    __tablename__ = 'stock_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    holder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)  # 购买价格
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def current_value(self):
        """计算当前市值"""
        return float(self.company.current_price) * self.shares
    
    def profit_loss(self):
        """计算盈亏"""
        return self.current_value() - float(self.purchase_price) * self.shares 