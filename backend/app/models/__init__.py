from app import db
from datetime import datetime

class BaseModel(db.Model):
    """基础模型类，包含共用字段"""
    __abstract__ = True
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # 让子类可以选择是否继承 updated_at
    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, '__mapper_args__') or \
           'exclude_properties' not in cls.__mapper_args__ or \
           'updated_at' not in cls.__mapper_args__['exclude_properties']:
            cls.updated_at = db.Column(
                db.TIMESTAMP, 
                nullable=False,
                default=datetime.utcnow,
                onupdate=datetime.utcnow
            ) 