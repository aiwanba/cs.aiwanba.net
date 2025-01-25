from models import db, MarketAnalysis, CompanyAnalysis, TechnicalIndicator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class AnalysisService:
    """市场分析服务"""
    
    @staticmethod
    def calculate_market_analysis():
        """计算市场分析数据"""
        today = datetime.now().date()
        
        # 获取今日市场数据
        market_data = db.session.query(
            db.func.sum(CompanyAnalysis.close_price * Company.total_shares).label('market_value'),
            db.func.sum(CompanyAnalysis.volume).label('trading_volume'),
            db.func.count(CompanyAnalysis.company_id.distinct()).label('active_companies')
        ).join(Company).filter(CompanyAnalysis.date == today).first()
        
        # 计算价格指数
        base_date = today - timedelta(days=365)  # 一年前作为基期
        base_value = 1000  # 基期指数值
        
        current_index = (market_data.market_value / base_value) * 1000
        
        analysis = MarketAnalysis(
            date=today,
            market_value=market_data.market_value,
            trading_volume=market_data.trading_volume,
            active_companies=market_data.active_companies,
            price_index=current_index
        )
        
        try:
            db.session.add(analysis)
            db.session.commit()
            return True, analysis
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def calculate_technical_indicators(company_id):
        """计算技术指标"""
        # 获取历史数据
        history = CompanyAnalysis.query.filter_by(company_id=company_id)\
            .order_by(CompanyAnalysis.date.desc())\
            .limit(30).all()
            
        if len(history) < 20:
            return False, "历史数据不足"
            
        # 转换为pandas DataFrame
        df = pd.DataFrame([{
            'date': h.date,
            'close': float(h.close_price),
            'high': float(h.high_price),
            'low': float(h.low_price)
        } for h in history])
        
        # 计算移动平均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算KDJ
        low_min = df['low'].rolling(window=9).min()
        high_max = df['high'].rolling(window=9).max()
        df['rsv'] = (df['close'] - low_min) / (high_max - low_min) * 100
        df['kdj_k'] = df['rsv'].ewm(com=2).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        
        # 保存最新的技术指标
        latest = df.iloc[0]
        indicator = TechnicalIndicator(
            company_id=company_id,
            date=latest['date'],
            ma5=latest['ma5'],
            ma10=latest['ma10'],
            ma20=latest['ma20'],
            rsi=latest['rsi'],
            kdj_k=latest['kdj_k'],
            kdj_d=latest['kdj_d'],
            kdj_j=latest['kdj_j'],
            macd=latest['macd']
        )
        
        try:
            db.session.add(indicator)
            db.session.commit()
            return True, indicator
        except Exception as e:
            db.session.rollback()
            return False, str(e) 