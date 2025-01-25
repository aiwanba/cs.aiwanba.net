from app import db
from datetime import datetime
from enum import Enum

class NewsType(Enum):
    MARKET = 'market'          # 市场新闻
    COMPANY = 'company'        # 公司新闻
    INDUSTRY = 'industry'      # 行业新闻
    ECONOMIC = 'economic'      # 经济新闻
    REGULATORY = 'regulatory'  # 监管新闻
    SOCIAL = 'social'          # 社会新闻

class NewsSource(Enum):
    SYSTEM = 'system'          # 系统生成
    AI = 'ai'                  # AI生成
    PLAYER = 'player'          # 玩家触发
    MARKET = 'market'          # 市场事件

class NewsImpact(Enum):
    VERY_NEGATIVE = -2         # 极度负面
    NEGATIVE = -1              # 负面
    NEUTRAL = 0                # 中性
    POSITIVE = 1               # 正面
    VERY_POSITIVE = 2          # 极度正面

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    impact = db.Column(db.Integer)  # -2 到 2
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'))
    trigger_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, type, source, title, content, impact=0, **kwargs):
        if type not in [t.value for t in NewsType]:
            raise ValueError("Invalid news type")
        if source not in [s.value for s in NewsSource]:
            raise ValueError("Invalid news source")
        if impact not in [i.value for i in NewsImpact]:
            raise ValueError("Invalid impact value")
            
        self.type = type
        self.source = source
        self.title = title
        self.content = content
        self.impact = impact
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'source': self.source,
            'title': self.title,
            'content': self.content,
            'impact': self.impact,
            'company_id': self.company_id,
            'industry_id': self.industry_id,
            'trigger_user_id': self.trigger_user_id,
            'views': self.views,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

class NewsTemplate(db.Model):
    __tablename__ = 'news_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    title_template = db.Column(db.String(200), nullable=False)
    content_template = db.Column(db.Text, nullable=False)
    trigger_conditions = db.Column(db.JSON)  # 触发条件
    impact_factors = db.Column(db.JSON)      # 影响因素
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, type, title_template, content_template, 
                 trigger_conditions=None, impact_factors=None):
        self.type = type
        self.title_template = title_template
        self.content_template = content_template
        self.trigger_conditions = trigger_conditions or {}
        self.impact_factors = impact_factors or {} 