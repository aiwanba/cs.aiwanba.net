from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID长度固定为36字符
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)  # 自动更新时间
    
    # 一对多关系
    messages = db.relationship('Message', backref='conversation', 
                             lazy='dynamic', cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), 
                              db.ForeignKey('conversations.id'), 
                              nullable=False)  # 强制外键约束
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, 
                         index=True)  # 添加索引优化查询
    
    __table_args__ = (
        db.Index('idx_conv_time', conversation_id, timestamp),
    )
    
    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        } 