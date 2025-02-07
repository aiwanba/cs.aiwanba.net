from models import db
from datetime import datetime

class Shareholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # 持有股数
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'shares': self.shares,
            'created_at': self.created_at.isoformat()
        } 