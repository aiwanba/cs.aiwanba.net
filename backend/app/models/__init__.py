from app import db
from datetime import datetime

class BaseModel(db.Model):
    """基础模型类，包含共用字段"""
    __abstract__ = True
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 