from flask import Blueprint, jsonify, request
from .models import db, User, Stock, Portfolio

main = Blueprint('main', __name__)

@main.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取所有股票信息"""
    stocks = Stock.query.all()
    return jsonify([{
        'id': stock.id,
        'symbol': stock.symbol,
        'name': stock.name,
        'current_price': stock.current_price,
        'last_updated': stock.last_updated
    } for stock in stocks])

@main.route('/api/portfolio/<int:user_id>', methods=['GET'])
def get_portfolio(user_id):
    """获取用户投资组合"""
    portfolios = Portfolio.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'stock_id': p.stock_id,
        'shares': p.shares,
        'average_price': p.average_price
    } for p in portfolios]) 