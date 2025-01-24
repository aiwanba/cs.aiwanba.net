from flask import Blueprint, request, jsonify
from services.ai_trading_service import AITradingService
from models import db

ai_trading_bp = Blueprint('ai_trading', __name__)

@ai_trading_bp.route('/traders', methods=['POST'])
def create_ai_trader():
    """创建AI交易员"""
    data = request.get_json()
    user_id = data.get('user_id')
    strategy_id = data.get('strategy_id')
    
    if not all([user_id, strategy_id]):
        return jsonify({'error': '缺少必要参数'}), 400
        
    try:
        ai_trader = AITradingService.create_ai_trader(user_id, strategy_id)
        return jsonify({
            'message': 'AI交易员创建成功',
            'ai_trader_id': ai_trader.id
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_trading_bp.route('/traders/<int:ai_trader_id>/execute', methods=['POST'])
def execute_trading_strategy(ai_trader_id):
    """执行交易策略"""
    try:
        order = AITradingService.execute_trading_strategy(ai_trader_id)
        return jsonify({
            'message': '交易策略执行成功',
            'order_id': order.id
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 