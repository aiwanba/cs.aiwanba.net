from extensions import db
from datetime import datetime
from flask import current_app

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    total_shares = db.Column(db.Integer, nullable=False)  # 总股本
    current_price = db.Column(db.Numeric(10, 2), nullable=False)  # 当前股价
    cash_balance = db.Column(db.Numeric(20, 2), default=0)  # 公司现金
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    owner = db.relationship('User', backref='owned_companies')
    stocks = db.relationship('Stock', backref='company', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典格式"""
        try:
            return {
                'id': self.id,
                'name': self.name,
                'industry': self.industry,
                'total_shares': self.total_shares,
                'current_price': float(self.current_price) if self.current_price else 0,
                'cash_balance': float(self.cash_balance) if self.cash_balance else 0,
                'owner_id': self.owner_id,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
            }
        except Exception as e:
            current_app.logger.error(f"Company.to_dict 失败: {str(e)}")
            raise 