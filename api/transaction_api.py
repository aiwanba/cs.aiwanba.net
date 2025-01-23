from flask import Blueprint, request, jsonify
from services.transaction_service import TransactionService
from app import db

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/market-order', methods=['POST'])
def create_market_order():
    """创建市价单"""
    data = request.get_json()
    company_id = data.get('company_id')
    stock_id = data.get('stock_id')
    shares = data.get('shares')
    is_buy = data.get('is_buy')
    
    if not all([company_id, stock_id, shares, is_buy is not None]):
        return jsonify({'error': '参数不完整'}), 400
    
    try:
        transaction = TransactionService.create_market_order(
            company_id=company_id,
            stock_id=stock_id,
            shares=shares,
            is_buy=is_buy
        )
        return jsonify({
            'message': '交易成功',
            'transaction_id': transaction.id
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/limit-order', methods=['POST'])
def create_limit_order():
    """创建限价单"""
    data = request.get_json()
    company_id = data.get('company_id')
    stock_id = data.get('stock_id')
    shares = data.get('shares')
    price = data.get('price')
    is_buy = data.get('is_buy')
    
    if not all([company_id, stock_id, shares, price, is_buy is not None]):
        return jsonify({'error': '参数不完整'}), 400
    
    try:
        order = TransactionService.create_limit_order(
            company_id=company_id,
            stock_id=stock_id,
            shares=shares,
            price=price,
            is_buy=is_buy
        )
        return jsonify({
            'message': '订单创建成功',
            'order_id': order.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消限价单"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        if order.status != 'pending':
            return jsonify({'error': '只能取消未完成的订单'}), 400
        
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': '订单已取消'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/history', methods=['GET'])
def get_transaction_history():
    """获取交易历史"""
    company_id = request.args.get('company_id')
    stock_id = request.args.get('stock_id')
    
    query = Transaction.query
    
    if company_id:
        query = query.filter(
            (Transaction.buyer_company_id == company_id) |
            (Transaction.seller_company_id == company_id)
        )
    
    if stock_id:
        query = query.filter_by(stock_id=stock_id)
    
    transactions = query.order_by(Transaction.created_at.desc()).all()
    
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