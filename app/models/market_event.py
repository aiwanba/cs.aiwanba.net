from app import db
from datetime import datetime
from enum import Enum

class EventType(Enum):
    PRICE_SURGE = 'price_surge'           # 价格暴涨
    PRICE_CRASH = 'price_crash'           # 价格暴跌
    HIGH_VOLATILITY = 'high_volatility'   # 高波动性
    VOLUME_SPIKE = 'volume_spike'         # 交易量激增
    MARKET_MANIPULATION = 'manipulation'   # 市场操纵
    INSIDER_TRADING = 'insider_trading'   # 内幕交易
    COMPANY_NEWS = 'company_news'         # 公司新闻
    MARKET_NEWS = 'market_news'           # 市场新闻
    AI_BEHAVIOR = 'ai_behavior'           # AI异常行为
    REGULATORY = 'regulatory'             # 监管事件

class EventSeverity(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class MarketEvent(db.Model):
    __tablename__ = 'market_events'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    impact_score = db.Column(db.Float)  # -1.0 到 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, type, severity, title, description, impact_score, 
                 company_id=None, expires_at=None):
        if type not in [e.value for e in EventType]:
            raise ValueError("Invalid event type")
        if severity not in [s.value for s in EventSeverity]:
            raise ValueError("Invalid severity level")
            
        self.type = type
        self.severity = severity
        self.company_id = company_id
        self.title = title
        self.description = description
        self.impact_score = max(min(impact_score, 1.0), -1.0)  # 限制在-1到1之间
        self.expires_at = expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'severity': self.severity,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'impact_score': self.impact_score,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        } 