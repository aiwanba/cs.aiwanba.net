from datetime import datetime
from apps.extensions import db

class News(db.Model):
    """新闻模型"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'market' 或 'company'
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # 可以为空（市场新闻）
    impact = db.Column(db.Float)  # 新闻影响因子（正负表示影响方向）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def apply_market_effect(self):
        """应用新闻效应到市场"""
        if self.company_id and self.impact:
            self.company.update_price(
                float(self.company.current_price) * (1 + self.impact)
            ) 