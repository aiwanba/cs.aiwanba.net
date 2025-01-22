from extensions import app, db
from models import User, Stock, Transaction
import random

def init_database():
    # 删除所有表（谨慎使用，会清空数据）
    db.drop_all()
    
    # 创建所有表
    db.create_all()

    # 添加初始数据（可选）
    # 创建初始用户
    admin_user = User(username='admin', password='admin123')
    db.session.add(admin_user)

    # 创建AI用户，初始资金为1亿
    ai_user = User(username='ai', password='ai123', balance=100000000.0)
    db.session.add(ai_user)

    # 创建初始股票
    stocks = [
        Stock(name='科技公司A', symbol='TECH-A', price=100.0),
        Stock(name='能源公司B', symbol='ENER-B', price=50.0),
        Stock(name='医疗公司C', symbol='MEDI-C', price=75.0),
        Stock(name='金融公司D', symbol='FINA-D', price=120.0),
        Stock(name='零售公司E', symbol='RETA-E', price=30.0),
        Stock(name='制造公司F', symbol='MANU-F', price=80.0),
        Stock(name='电信公司G', symbol='TELC-G', price=90.0),
        Stock(name='食品公司H', symbol='FOOD-H', price=40.0),
        Stock(name='汽车公司I', symbol='AUTO-I', price=60.0),
        Stock(name='航空公司J', symbol='AIRL-J', price=70.0)
    ]
    db.session.add_all(stocks)

    # 提交更改
    db.session.commit()

    # 为AI用户添加初始股票持仓
    with app.app_context():
        ai_user = User.query.filter_by(username='ai').first()
        if ai_user:
            # 为AI用户随机买入一些股票
            for stock in Stock.query.all():
                if random.choice([True, False]):  # 随机决定是否买入
                    quantity = random.randint(1, 10)
                    transaction = Transaction(
                        user_id=ai_user.id,
                        stock_id=stock.id,
                        quantity=quantity,
                        price=stock.price,
                        type='buy'
                    )
                    db.session.add(transaction)
            db.session.commit()

    print("数据库初始化完成！")

if __name__ == '__main__':
    init_database() 