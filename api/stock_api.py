from flask import Blueprint, jsonify
from models.stock import Stock
from datetime import datetime, timedelta

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/prices', methods=['GET'])
def get_stock_prices():
    """获取所有股票当前价格"""
    stocks = Stock.query.all()
    return jsonify({
        'stocks': [{
            'id': stock.id,
            'company_id': stock.company_id,
            'current_price': stock.current_price,
            'updated_at': stock.updated_at.isoformat() if stock.updated_at else None
        } for stock in stocks]
    })

@stock_bp.route('/prices/<int:stock_id>', methods=['GET'])
def get_stock_price(stock_id):
    """获取单个股票价格"""
    stock = Stock.query.get_or_404(stock_id)
    return jsonify({
        'id': stock.id,
        'company_id': stock.company_id,
        'current_price': stock.current_price,
        'updated_at': stock.updated_at.isoformat() if stock.updated_at else None
    })

@stock_bp.route('/prices/<int:stock_id>/history', methods=['GET'])
def get_stock_price_history(stock_id):
    """获取股票价格历史"""
    # 获取最近24小时的交易记录来显示价格变化
    recent_time = datetime.utcnow() - timedelta(hours=24)
    transactions = Transaction.query.filter(
        Transaction.stock_id == stock_id,
        Transaction.status == 'completed',
        Transaction.created_at >= recent_time
    ).order_by(Transaction.created_at.asc()).all()
    
    return jsonify({
        'price_history': [{
            'price': t.price,
            'shares': t.shares,
            'timestamp': t.created_at.isoformat()
        } for t in transactions]
    }) 