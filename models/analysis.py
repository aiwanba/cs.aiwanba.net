from datetime import datetime
from . import db

class MarketAnalysis(db.Model):
    """市场分析数据"""
    __tablename__ = 'market_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    market_value = db.Column(db.Numeric(20, 2), nullable=False)  # 总市值
    trading_volume = db.Column(db.Integer, nullable=False)  # 成交量
    active_companies = db.Column(db.Integer, nullable=False)  # 活跃公司数
    price_index = db.Column(db.Numeric(10, 2), nullable=False)  # 价格指数
    created_at = db.Column(db.DateTime, default=datetime.now)

class CompanyAnalysis(db.Model):
    """公司分析数据"""
    __tablename__ = 'company_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Numeric(10, 2), nullable=False)
    close_price = db.Column(db.Numeric(10, 2), nullable=False)
    high_price = db.Column(db.Numeric(10, 2), nullable=False)
    low_price = db.Column(db.Numeric(10, 2), nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    turnover = db.Column(db.Numeric(20, 2), nullable=False)
    pe_ratio = db.Column(db.Numeric(10, 2))  # 市盈率
    pb_ratio = db.Column(db.Numeric(10, 2))  # 市净率
    created_at = db.Column(db.DateTime, default=datetime.now)

class TechnicalIndicator(db.Model):
    """技术指标数据"""
    __tablename__ = 'technical_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    ma5 = db.Column(db.Numeric(10, 2))  # 5日均线
    ma10 = db.Column(db.Numeric(10, 2))  # 10日均线
    ma20 = db.Column(db.Numeric(10, 2))  # 20日均线
    rsi = db.Column(db.Numeric(10, 2))  # RSI指标
    kdj_k = db.Column(db.Numeric(10, 2))  # KDJ指标K值
    kdj_d = db.Column(db.Numeric(10, 2))  # KDJ指标D值
    kdj_j = db.Column(db.Numeric(10, 2))  # KDJ指标J值
    macd = db.Column(db.Numeric(10, 2))  # MACD指标
    created_at = db.Column(db.DateTime, default=datetime.now) 