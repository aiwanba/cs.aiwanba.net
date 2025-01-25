from app import db
from datetime import datetime
from enum import Enum

class IndicatorType(Enum):
    MA = 'ma'                # 移动平均线
    EMA = 'ema'              # 指数移动平均线
    MACD = 'macd'            # 移动平均收敛散度
    RSI = 'rsi'              # 相对强弱指标
    BOLL = 'boll'            # 布林带
    KDJ = 'kdj'              # 随机指标
    VOL = 'vol'              # 成交量
    OBV = 'obv'              # 能量潮指标

class AnalysisReport(db.Model):
    __tablename__ = 'analysis_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # technical, fundamental, market_depth
    target_id = db.Column(db.Integer, nullable=False)  # 分析目标ID（公司/行业）
    target_type = db.Column(db.String(20), nullable=False)  # company, industry
    data = db.Column(db.JSON, nullable=False)  # 分析数据
    summary = db.Column(db.Text)  # 分析总结
    recommendations = db.Column(db.JSON)  # 投资建议
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'data': self.data,
            'summary': self.summary,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat()
        }

class TechnicalIndicator(db.Model):
    __tablename__ = 'technical_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    period = db.Column(db.Integer, nullable=False)  # 计算周期
    values = db.Column(db.JSON, nullable=False)  # 指标值
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, stock_id, type, period):
        if type not in [t.value for t in IndicatorType]:
            raise ValueError("Invalid indicator type")
        self.stock_id = stock_id
        self.type = type
        self.period = period
        self.values = {}

class MarketDepth(db.Model):
    __tablename__ = 'market_depth'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    buy_orders = db.Column(db.JSON, nullable=False)  # 买单深度
    sell_orders = db.Column(db.JSON, nullable=False)  # 卖单深度
    total_buy_volume = db.Column(db.Float, default=0.0)
    total_sell_volume = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, stock_id):
        self.stock_id = stock_id
        self.buy_orders = {}
        self.sell_orders = {} 