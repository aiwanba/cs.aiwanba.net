from flask import Blueprint, request, jsonify
from services.ai_trading_service import AITradingService
from models.ai_strategy import AITrader
from app import db

ai_trading_bp = Blueprint('ai_trading', __name__)

@ai_trading_bp.route('/traders', methods=['POST'])
def create_ai_trader():
    """创建AI交易者"""
    data = request.get_json()
    user_id = data.get('user_id')
    strategy_type = data.get('strategy_type')
    initial_cash = data.get('initial_cash')
    
    if not all([user_id, strategy_type, initial_cash]):
        return jsonify({'error': '参数不完整'}), 400
        
    try:
        trader = AITradingService.create_ai_trader(
            user_id=user_id,
            strategy_type=strategy_type,
            initial_cash=initial_cash
        )
        return jsonify({
            'message': 'AI交易者创建成功',
            'trader_id': trader.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_trading_bp.route('/traders/<int:trader_id>/status', methods=['GET'])
def get_trader_status(trader_id):
    """获取AI交易者状态"""
    trader = AITrader.query.get_or_404(trader_id)
    return jsonify({
        'id': trader.id,
        'is_active': trader.is_active,
        'current_cash': trader.current_cash,
        'total_value': trader.total_value,
        'total_trades': trader.total_trades,
        'successful_trades': trader.successful_trades,
        'total_profit': trader.total_profit,
        'strategy': {
            'type': trader.strategy.type,
            'name': trader.strategy.name,
            'description': trader.strategy.description
        }
    })

@ai_trading_bp.route('/traders/<int:trader_id>/toggle', methods=['POST'])
def toggle_trader_status(trader_id):
    """切换AI交易者状态"""
    trader = AITrader.query.get_or_404(trader_id)
    trader.is_active = not trader.is_active
    db.session.commit()
    
    return jsonify({
        'message': f"AI交易者已{'启动' if trader.is_active else '停止'}",
        'is_active': trader.is_active
    })

@ai_trading_bp.route('/analysis/market/<int:stock_id>', methods=['GET'])
def analyze_market(stock_id):
    """获取市场分析数据"""
    analysis = AITradingService.analyze_market(stock_id)
    if not analysis:
        return jsonify({'error': '无法获取市场数据'}), 404
    return jsonify(analysis) 