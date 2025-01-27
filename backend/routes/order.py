from flask import jsonify, request
from . import stock_bp
from services.matching import MatchingEngine
from app import db

@stock_bp.route('/order/create', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.get_json()
    
    required_fields = ['company_id', 'user_id', 'order_type', 'amount', 'price']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        order = MatchingEngine.create_order(
            company_id=data['company_id'],
            user_id=data['user_id'],
            order_type=data['order_type'],
            amount=data['amount'],
            price=data['price']
        )
        
        return jsonify({
            'message': '订单创建成功',
            'order': {
                'id': order.id,
                'type': order.order_type,
                'amount': order.amount,
                'price': float(order.price),
                'status': order.status
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '创建订单失败'}), 500 