from flask import Blueprint, request, jsonify
from services.transaction_service import TransactionService
from models import db

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/market-order', methods=['POST'])
def create_market_order():
    """创建市价单"""
    data = request.get_json()
    company_id = data.get('company_id')
    stock_id = data.get('stock_id')
    order_type = data.get('order_type')  # 'buy' or 'sell'
    shares = data.get('shares')
    price = data.get('price')
    
    if not all([company_id, stock_id, order_type, shares, price]):
        return jsonify({'error': '缺少必要参数'}), 400
        
    try:
        order = TransactionService.create_market_order(company_id, stock_id, order_type, shares, price)
        return jsonify({
            'message': '市价单创建成功',
            'order_id': order.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/orders/<int:order_id>/execute', methods=['POST'])
def execute_order(order_id):
    """执行订单"""
    try:
        order = TransactionService.execute_order(order_id)
        return jsonify({
            'message': '订单执行成功',
            'order_id': order.id,
            'status': order.status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions/<int:company_id>', methods=['GET'])
def get_transaction_history(company_id):
    """获取交易历史"""
    try:
        transactions = TransactionService.get_transaction_history(company_id)
        return jsonify({
            'transactions': [{
                'id': t.id,
                'buyer_id': t.buyer_company_id,
                'seller_id': t.seller_company_id,
                'stock_id': t.stock_id,
                'shares': t.shares,
                'price': t.price,
                'total_amount': t.total_amount,
                'status': t.status,
                'created_at': t.created_at.isoformat(),
                'completed_at': t.completed_at.isoformat() if t.completed_at else None
            } for t in transactions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 