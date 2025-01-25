from datetime import datetime
from app import db

class Company(db.Model):
    """公司模型"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_shares = db.Column(db.Integer, nullable=False)  # 总股数
    available_shares = db.Column(db.Integer, nullable=False)  # 可交易股数
    current_price = db.Column(db.Numeric(10, 2), nullable=False)  # 当前股价
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系
    stocks = db.relationship('StockHolding', backref='company', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='company', lazy='dynamic')
    news = db.relationship('News', backref='company', lazy='dynamic')
    
    def market_value(self):
        """计算市值"""
        return float(self.current_price) * self.total_shares
    
    def update_price(self, new_price):
        """更新股价"""
        self.current_price = new_price
        db.session.commit() 