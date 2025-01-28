from . import db, BaseModel
from datetime import datetime, timedelta

class Message(BaseModel):
    """消息模型"""
    __tablename__ = 'messages'
    
    type = db.Column(db.TINYINT, nullable=False)  # 1-系统公告，2-公司公告，3-交易提醒，4-风险预警
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    related_id = db.Column(db.BigInteger)  # 关联ID（如公司ID、交易ID等）
    priority = db.Column(db.TINYINT, default=3)  # 1-高，2-中，3-低
    expire_at = db.Column(db.TIMESTAMP)  # 过期时间
    status = db.Column(db.TINYINT, default=1)  # 1-有效，0-已过期
    
    # 关联关系
    recipients = db.relationship('MessageRecipient', backref='message', lazy=True)
    
    def __init__(self, type, title, content, related_id=None, priority=3, expire_days=1):
        self.type = type
        self.title = title
        self.content = content
        self.related_id = related_id
        self.priority = priority
        self.expire_at = datetime.utcnow() + timedelta(days=expire_days)
    
    def is_expired(self):
        """检查消息是否过期"""
        return datetime.utcnow() > self.expire_at if self.expire_at else False
    
    def mark_expired(self):
        """标记消息为已过期"""
        self.status = 0
        db.session.commit()
    
    def broadcast(self, user_ids):
        """广播消息给指定用户"""
        recipients = []
        for user_id in user_ids:
            recipient = MessageRecipient(message_id=self.id, user_id=user_id)
            recipients.append(recipient)
        db.session.bulk_save_objects(recipients)
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'related_id': self.related_id,
            'priority': self.priority,
            'expire_at': self.expire_at.isoformat() if self.expire_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class MessageRecipient(BaseModel):
    """消息接收者模型"""
    __tablename__ = 'message_recipients'
    
    message_id = db.Column(db.BigInteger, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    is_read = db.Column(db.TINYINT, default=0)  # 0-未读，1-已读
    
    def mark_read(self):
        """标记消息为已读"""
        self.is_read = 1
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'message': self.message.to_dict() if self.message else None
        } 