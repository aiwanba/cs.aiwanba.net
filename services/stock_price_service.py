from models import db
from models.stock import Stock
from models.transaction import Transaction
from datetime import datetime, timedelta
import random

class StockPriceService:
    """股票价格服务"""
    
    @staticmethod
    def update_stock_prices():
        """更新所有股票价格"""
        stocks = Stock.query.all()
        for stock in stocks:
            # 获取最近24小时的交易数据
            recent_time = datetime.utcnow() - timedelta(hours=24)
            transactions = Transaction.query.filter(
                Transaction.stock_id == stock.id,
                Transaction.status == 'completed',
                Transaction.created_at >= recent_time
            ).order_by(Transaction.created_at.desc()).all()
            
            if transactions:
                # 根据最近交易价格更新
                last_price = transactions[0].price
                # 随机波动
                fluctuation = random.uniform(-0.05, 0.05)  # ±5%
                new_price = last_price * (1 + fluctuation)
            else:
                # 如果没有交易记录，随机生成价格
                new_price = random.uniform(10, 100)
            
            # 更新股票价格
            stock.current_price = new_price
            db.session.add(stock)
        
        db.session.commit()
        return len(stocks)

    @staticmethod
    def get_stock_price(stock_id):
        """获取股票价格"""
        stock = Stock.query.get(stock_id)
        if stock:
            return stock.current_price
        return None 