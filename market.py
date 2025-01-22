import random
from extensions import app, db
from models import Stock

def simulate_market():
    """
    模拟股票价格波动
    """
    with app.app_context():  # 手动推送应用上下文
        stocks = Stock.query.all()
        for stock in stocks:
            # 生成一个随机的价格波动（-5%到+5%）
            fluctuation = random.uniform(-0.05, 0.05)
            new_price = stock.price * (1 + fluctuation)
            
            # 确保价格不会低于0
            if new_price < 0:
                new_price = 0
            
            # 更新股票价格
            stock.price = new_price
            db.session.add(stock)
        
        db.session.commit()
        print("股票价格波动模拟完成！") 