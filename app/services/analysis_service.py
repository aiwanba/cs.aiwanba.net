from app import db
from app.models.analysis import (
    AnalysisReport, TechnicalIndicator, MarketDepth,
    IndicatorType
)
from app.models.stock import Stock, Transaction
from app.models.company import Company
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import talib

class AnalysisService:
    def __init__(self):
        self.indicator_cache = {}
        self.depth_cache = {}
        
    def generate_technical_analysis(self, stock_id, indicators=None):
        """生成技术分析"""
        try:
            # 获取历史数据
            stock_data = self._get_stock_data(stock_id)
            if not stock_data.empty:
                # 计算技术指标
                analysis = {}
                
                # 如果没有指定指标，计算所有指标
                if not indicators:
                    indicators = [t.value for t in IndicatorType]
                
                for indicator in indicators:
                    values = self._calculate_indicator(stock_data, indicator)
                    if values is not None:
                        analysis[indicator] = values
                
                # 生成分析报告
                report = AnalysisReport(
                    type='technical',
                    target_id=stock_id,
                    target_type='company',
                    data=analysis,
                    summary=self._generate_technical_summary(analysis),
                    recommendations=self._generate_recommendations(analysis)
                )
                
                db.session.add(report)
                db.session.commit()
                
                return report
                
        except Exception as e:
            db.session.rollback()
            print(f"Technical analysis error: {str(e)}")
            return None
    
    def analyze_market_depth(self, stock_id):
        """分析市场深度"""
        try:
            depth = MarketDepth.query.filter_by(stock_id=stock_id).first()
            if not depth:
                return None
            
            analysis = {
                'buy_pressure': self._calculate_buy_pressure(depth),
                'sell_pressure': self._calculate_sell_pressure(depth),
                'order_imbalance': self._calculate_order_imbalance(depth),
                'price_levels': self._analyze_price_levels(depth)
            }
            
            report = AnalysisReport(
                type='market_depth',
                target_id=stock_id,
                target_type='company',
                data=analysis,
                summary=self._generate_depth_summary(analysis)
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report
            
        except Exception as e:
            print(f"Market depth analysis error: {str(e)}")
            return None
    
    def _get_stock_data(self, stock_id):
        """获取股票历史数据"""
        # 获取最近100个交易日的数据
        transactions = Transaction.query.filter_by(
            stock_id=stock_id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(100).all()
        
        if not transactions:
            return pd.DataFrame()
        
        # 转换为DataFrame
        data = pd.DataFrame([
            {
                'date': t.created_at,
                'price': t.price,
                'volume': t.volume
            }
            for t in transactions
        ])
        
        return data.sort_values('date')
    
    def _calculate_indicator(self, data, indicator_type):
        """计算技术指标"""
        try:
            prices = data['price'].values
            volumes = data['volume'].values
            
            if indicator_type == IndicatorType.MA.value:
                return {
                    'MA5': talib.MA(prices, timeperiod=5).tolist(),
                    'MA10': talib.MA(prices, timeperiod=10).tolist(),
                    'MA20': talib.MA(prices, timeperiod=20).tolist()
                }
            elif indicator_type == IndicatorType.MACD.value:
                macd, signal, hist = talib.MACD(prices)
                return {
                    'MACD': macd.tolist(),
                    'Signal': signal.tolist(),
                    'Histogram': hist.tolist()
                }
            elif indicator_type == IndicatorType.RSI.value:
                return {
                    'RSI': talib.RSI(prices).tolist()
                }
            elif indicator_type == IndicatorType.BOLL.value:
                upper, middle, lower = talib.BBANDS(prices)
                return {
                    'Upper': upper.tolist(),
                    'Middle': middle.tolist(),
                    'Lower': lower.tolist()
                }
            # ... 其他指标的计算 ...
            
        except Exception as e:
            print(f"Indicator calculation error: {str(e)}")
            return None
    
    def _calculate_buy_pressure(self, depth):
        """计算买入压力"""
        total_volume = depth.total_buy_volume + depth.total_sell_volume
        if total_volume == 0:
            return 0
        return depth.total_buy_volume / total_volume
    
    def _calculate_sell_pressure(self, depth):
        """计算卖出压力"""
        total_volume = depth.total_buy_volume + depth.total_sell_volume
        if total_volume == 0:
            return 0
        return depth.total_sell_volume / total_volume
    
    def _calculate_order_imbalance(self, depth):
        """计算订单失衡度"""
        total_volume = depth.total_buy_volume + depth.total_sell_volume
        if total_volume == 0:
            return 0
        return (depth.total_buy_volume - depth.total_sell_volume) / total_volume
    
    def _analyze_price_levels(self, depth):
        """分析价格水平"""
        return {
            'buy_levels': self._analyze_order_distribution(depth.buy_orders),
            'sell_levels': self._analyze_order_distribution(depth.sell_orders)
        }
    
    def _analyze_order_distribution(self, orders):
        """分析订单分布"""
        if not orders:
            return {}
            
        prices = list(orders.keys())
        volumes = list(orders.values())
        
        return {
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(p * v for p, v in zip(prices, volumes)) / sum(volumes),
            'total_volume': sum(volumes),
            'price_levels': len(prices)
        }
    
    def _generate_technical_summary(self, analysis):
        """生成技术分析总结"""
        # TODO: 实现更智能的分析总结
        return "根据技术指标分析，市场呈现..."
    
    def _generate_depth_summary(self, analysis):
        """生成深度分析总结"""
        # TODO: 实现更智能的深度分析总结
        return "根据市场深度分析，当前买卖压力..."
    
    def _generate_recommendations(self, analysis):
        """生成投资建议"""
        # TODO: 实现更智能的投资建议
        return {
            'action': 'hold',
            'confidence': 0.6,
            'reasons': ['技术指标显示市场中性']
        } 