from flask import jsonify, request
from . import stock_bp
from services.stock import StockService
from app import db

@stock_bp.route('/order/create', methods=['POST'])
def create_order():
    """创建卖单"""
    data = request.get_json()
    
    required_fields = ['company_id', 'seller_id', 'amount', 'price']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        order = StockService.create_order(
            company_id=data['company_id'],
            seller_id=data['seller_id'],
            amount=data['amount'],
            price=data['price']
        )
        
        return jsonify({
            'message': '卖单创建成功',
            'order': order
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '创建卖单失败'}), 500

@stock_bp.route('/trade', methods=['POST'])
def execute_trade():
    """执行交易"""
    data = request.get_json()
    
    required_fields = ['company_id', 'seller_id', 'buyer_id', 'amount', 'price']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        transaction = StockService.execute_trade(
            company_id=data['company_id'],
            seller_id=data['seller_id'],
            buyer_id=data['buyer_id'],
            amount=data['amount'],
            price=data['price']
        )
        
        return jsonify({
            'message': '交易执行成功',
            'transaction': {
                'id': transaction.id,
                'amount': transaction.amount,
                'price': float(transaction.price),
                'created_at': transaction.created_at.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '交易执行失败'}), 500 