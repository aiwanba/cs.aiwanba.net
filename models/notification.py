from app import db
from datetime import datetime

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # system, price, transaction, company
    level = db.Column(db.String(10), nullable=False)  # info, warning, error
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_id = db.Column(db.Integer)  # 相关的公司ID或用户ID
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'level': self.level,
            'title': self.title,
            'content': self.content,
            'target_id': self.target_id,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        } 