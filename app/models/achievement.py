from app import db
from datetime import datetime
from enum import Enum

class AchievementCategory(Enum):
    TRADING = 'trading'          # 交易成就
    INVESTMENT = 'investment'    # 投资成就
    SOCIAL = 'social'           # 社交成就
    COMPANY = 'company'         # 公司成就
    SPECIAL = 'special'         # 特殊成就

class AchievementRarity(Enum):
    COMMON = 'common'           # 普通
    UNCOMMON = 'uncommon'       # 不常见
    RARE = 'rare'              # 稀有
    EPIC = 'epic'              # 史诗
    LEGENDARY = 'legendary'     # 传说

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, default=0)  # 成就点数
    icon_url = db.Column(db.String(200))
    conditions = db.Column(db.JSON)  # 达成条件
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, description, category, rarity, points=0, 
                 icon_url=None, conditions=None):
        if category not in [c.value for c in AchievementCategory]:
            raise ValueError("Invalid achievement category")
        if rarity not in [r.value for r in AchievementRarity]:
            raise ValueError("Invalid achievement rarity")
            
        self.name = name
        self.description = description
        self.category = category
        self.rarity = rarity
        self.points = points
        self.icon_url = icon_url
        self.conditions = conditions or {}

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 完成进度
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    # 联合唯一索引确保用户不会重复获得同一成就
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)

class AchievementProgress(db.Model):
    __tablename__ = 'achievement_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    metric = db.Column(db.String(50), nullable=False)  # 统计指标
    value = db.Column(db.Float, default=0.0)  # 当前值
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一索引确保每个用户的每个指标只有一条记录
    __table_args__ = (db.UniqueConstraint('user_id', 'category', 'metric', name='unique_user_progress'),) 