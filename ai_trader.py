import random
from extensions import app, db
from models import User, Stock, Transaction

def ai_trade():
    """
    AI对手的自动交易策略
    """
    with app.app_context():
        # 获取AI用户（假设AI用户的ID为1）
        ai_user = User.query.get(1)
        if not ai_user:
            print("AI用户不存在，请先创建AI用户！")
            return

        # 获取所有股票
        stocks = Stock.query.all()
        if not stocks:
            print("没有可交易的股票！")
            return

        # 随机选择一支股票
        stock = random.choice(stocks)

        # 随机决定买入或卖出
        action = random.choice(['buy', 'sell'])

        # 随机决定交易数量（1到10股）
        quantity = random.randint(1, 10)

        if action == 'buy':
            # 计算总成本
            total_cost = stock.price * quantity

            # 检查AI用户余额是否足够
            if ai_user.balance >= total_cost:
                # 更新AI用户余额
                ai_user.balance -= total_cost
                db.session.add(ai_user)

                # 创建交易记录
                transaction = Transaction(
                    user_id=ai_user.id,
                    stock_id=stock.id,
                    quantity=quantity,
                    price=stock.price,
                    type='buy'
                )
                db.session.add(transaction)
                db.session.commit()
                print(f"AI用户买入{quantity}股{stock.name}，花费{total_cost}元。")
            else:
                print("AI用户余额不足，无法买入股票。")
        else:
            # 检查AI用户是否持有足够的股票
            holdings = Transaction.query.filter_by(user_id=ai_user.id, stock_id=stock.id, type='buy').all()
            total_holdings = sum(t.quantity for t in holdings)

            if total_holdings >= quantity:
                # 更新AI用户余额
                total_income = stock.price * quantity
                ai_user.balance += total_income
                db.session.add(ai_user)

                # 创建交易记录
                transaction = Transaction(
                    user_id=ai_user.id,
                    stock_id=stock.id,
                    quantity=quantity,
                    price=stock.price,
                    type='sell'
                )
                db.session.add(transaction)
                db.session.commit()
                print(f"AI用户卖出{quantity}股{stock.name}，获得{total_income}元。")
            else:
                print("AI用户持有股票数量不足，无法卖出股票。") 