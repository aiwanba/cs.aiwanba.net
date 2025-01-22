import random
from extensions import app, db
from models import User, Stock, Transaction

def ai_trade():
    """
    AI对手的自动交易策略
    """
    with app.app_context():
        # 获取AI用户（通过用户名查找）
        ai_user = User.query.filter_by(username='ai').first()
        if not ai_user:
            print("AI用户不存在，请先创建AI用户！")
            return

        # 获取所有股票
        stocks = Stock.query.all()
        if not stocks:
            print("没有可交易的股票！")
            return

        # 获取AI用户当前持有的股票
        holdings = Transaction.query.filter_by(user_id=ai_user.id, type='buy').all()
        held_stocks = {t.stock_id for t in holdings}  # 获取AI用户持有的股票ID集合

        # 如果AI用户持有股票，优先选择持有的股票
        if held_stocks:
            stock = random.choice([Stock.query.get(sid) for sid in held_stocks])
        else:
            # 如果AI用户没有持有任何股票，随机选择一支股票进行买入
            stock = random.choice(stocks)

        # 获取该股票的历史交易记录
        transactions = Transaction.query.filter_by(stock_id=stock.id).order_by(Transaction.timestamp.desc()).all()

        # 计算股票价格的平均波动
        price_changes = []
        for i in range(1, len(transactions)):
            price_changes.append(transactions[i-1].price - transactions[i].price)
        avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0

        # 根据价格波动决定买入或卖出
        if avg_price_change > 0:  # 价格上涨趋势
            action = 'buy' if random.random() < 0.7 else 'sell'  # 70%概率买入
        else:  # 价格下跌趋势
            action = 'sell' if random.random() < 0.7 else 'buy'  # 70%概率卖出

        # 如果AI用户没有持有该股票，只能买入
        if stock.id not in held_stocks:
            action = 'buy'

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