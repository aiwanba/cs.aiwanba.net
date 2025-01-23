from app import db
from models.stock import Stock
from models.transaction import Transaction
from datetime import datetime, timedelta
import numpy as np

class StockPriceService:
    """股票价格更新服务"""
    
    @staticmethod
    def calculate_new_price(stock_id):
        """
        计算新的股票价格
        使用加权移动平均价格(VWAP)和市场深度来计算
        """
        # 获取最近24小时的交易记录
        recent_time = datetime.utcnow() - timedelta(hours=24)
        transactions = Transaction.query.filter(
            Transaction.stock_id == stock_id,
            Transaction.status == 'completed',
            Transaction.created_at >= recent_time
        ).all()
        
        if not transactions:
            return None  # 无交易记录，保持原价
            
        # 计算成交量加权平均价格(VWAP)
        total_amount = sum(t.total_amount for t in transactions)
        total_shares = sum(t.shares for t in transactions)
        vwap = total_amount / total_shares if total_shares > 0 else None
        
        # 获取当前未完成的买卖订单
        buy_orders = Order.query.filter_by(
            stock_id=stock_id,
            order_type='buy',
            status='pending'
        ).all()
        
        sell_orders = Order.query.filter_by(
            stock_id=stock_id,
            order_type='sell',
            status='pending'
        ).all()
        
        # 计算买卖压力
        buy_pressure = sum(o.shares * o.price for o in buy_orders)
        sell_pressure = sum(o.shares * o.price for o in sell_orders)
        
        # 计算价格调整因子
        if buy_pressure + sell_pressure > 0:
            price_factor = buy_pressure / (buy_pressure + sell_pressure)
        else:
            price_factor = 0.5  # 无订单时保持中性
            
        # 获取当前价格
        stock = Stock.query.get(stock_id)
        current_price = stock.current_price
        
        if vwap is None:
            return current_price
            
        # 根据买卖压力调整价格
        # 价格因子大于0.5表示买压大，价格上涨
        # 价格因子小于0.5表示卖压大，价格下跌
        price_change = (price_factor - 0.5) * 0.1  # 最大涨跌幅为10%
        
        # 新价格为VWAP和当前价格的加权平均，再根据买卖压力调整
        new_price = (vwap * 0.7 + current_price * 0.3) * (1 + price_change)
        
        # 限制价格波动，防止剧烈波动
        max_change = current_price * 0.1  # 最大涨跌幅10%
        if new_price > current_price + max_change:
            new_price = current_price + max_change
        elif new_price < current_price - max_change:
            new_price = current_price - max_change
            
        return round(new_price, 2)
    
    @staticmethod
    def update_stock_price(stock_id):
        """更新股票价格"""
        new_price = StockPriceService.calculate_new_price(stock_id)
        if new_price is not None:
            stock = Stock.query.get(stock_id)
            stock.current_price = new_price
            stock.updated_at = datetime.utcnow()
            db.session.commit()
            return new_price
        return None
    
    @staticmethod
    def update_all_stock_prices():
        """更新所有股票价格"""
        stocks = Stock.query.all()
        updates = []
        for stock in stocks:
            new_price = StockPriceService.update_stock_price(stock.id)
            if new_price is not None:
                updates.append({
                    'stock_id': stock.id,
                    'new_price': new_price
                })
        return updates 