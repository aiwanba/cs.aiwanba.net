from datetime import datetime
from . import db

class NewsEvent(db.Model):
    """新闻事件"""
    __tablename__ = 'news_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # 新闻标题
    content = db.Column(db.Text, nullable=False)  # 新闻内容
    type = db.Column(db.String(20), nullable=False)  # 新闻类型：market, company, bank, global
    impact_type = db.Column(db.String(20))  # 影响类型：price, volume, interest, none
    impact_value = db.Column(db.Float)  # 影响值：正数表示上涨，负数表示下跌
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # 相关公司ID
    active = db.Column(db.Boolean, default=True)  # 是否生效中
    start_time = db.Column(db.DateTime, default=datetime.now)  # 生效开始时间
    end_time = db.Column(db.DateTime)  # 生效结束时间
    created_at = db.Column(db.DateTime, default=datetime.now)

class NewsComment(db.Model):
    """新闻评论"""
    __tablename__ = 'news_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联关系
    news = db.relationship('NewsEvent', backref='comments', lazy=True)
    user = db.relationship('User', backref='news_comments', lazy=True) 