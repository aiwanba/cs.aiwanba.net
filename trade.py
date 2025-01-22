from flask import Blueprint, request, jsonify
from models import db, User, Stock, Transaction

trade = Blueprint('trade', __name__)

# 买入股票
@trade.route('/buy', methods=['POST'])
def buy_stock():
    data = request.get_json()
    user_id = data.get('user_id')
    stock_id = data.get('stock_id')
    quantity = data.get('quantity')

    if not user_id or not stock_id or not quantity:
        return jsonify({'message': '用户ID、股票ID和数量不能为空'}), 400

    user = User.query.get(user_id)
    stock = Stock.query.get(stock_id)

    if not user or not stock:
        return jsonify({'message': '用户或股票不存在'}), 404

    total_cost = stock.price * quantity

    if user.balance < total_cost:
        return jsonify({'message': '余额不足'}), 400

    # 更新用户余额
    user.balance -= total_cost
    db.session.add(user)

    # 创建交易记录
    transaction = Transaction(
        user_id=user_id,
        stock_id=stock_id,
        quantity=quantity,
        price=stock.price,
        type='buy'
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': '买入成功', 'balance': user.balance}), 200

# 卖出股票
@trade.route('/sell', methods=['POST'])
def sell_stock():
    data = request.get_json()
    user_id = data.get('user_id')
    stock_id = data.get('stock_id')
    quantity = data.get('quantity')

    if not user_id or not stock_id or not quantity:
        return jsonify({'message': '用户ID、股票ID和数量不能为空'}), 400

    user = User.query.get(user_id)
    stock = Stock.query.get(stock_id)

    if not user or not stock:
        return jsonify({'message': '用户或股票不存在'}), 404

    # 检查用户是否持有足够的股票
    holdings = Transaction.query.filter_by(user_id=user_id, stock_id=stock_id, type='buy').all()
    total_holdings = sum(t.quantity for t in holdings)

    if total_holdings < quantity:
        return jsonify({'message': '持有股票数量不足'}), 400

    # 更新用户余额
    total_income = stock.price * quantity
    user.balance += total_income
    db.session.add(user)

    # 创建交易记录
    transaction = Transaction(
        user_id=user_id,
        stock_id=stock_id,
        quantity=quantity,
        price=stock.price,
        type='sell'
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': '卖出成功', 'balance': user.balance}), 200

@trade.route('/buy', methods=['GET'])
def buy_stock_get():
    return jsonify({'message': '请使用POST请求来买入股票'}), 405

@trade.route('/sell', methods=['GET'])
def sell_stock_get():
    return jsonify({'message': '请使用POST请求来卖出股票'}), 405 