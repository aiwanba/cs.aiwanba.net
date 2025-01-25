from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from apps.services.trading_service import TradingService
from apps.models.company import Company

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/buy', methods=['POST'])
@login_required
def buy_stock():
    """购买股票"""
    data = request.get_json()
    company = Company.query.get_or_404(data['company_id'])
    
    success, result = TradingService.buy_stock(
        current_user,
        company,
        int(data['shares']),
        float(data['price'])
    )
    
    if success:
        return jsonify({
            'message': '购买成功',
            'transaction': {
                'id': result.id,
                'shares': result.shares,
                'price': float(result.price),
                'total_amount': float(result.total_amount)
            }
        })
    return jsonify({'message': result}), 400

@trading_bp.route('/sell', methods=['POST'])
@login_required
def sell_stock():
    """出售股票"""
    data = request.get_json()
    company = Company.query.get_or_404(data['company_id'])
    
    success, result = TradingService.sell_stock(
        current_user,
        company,
        int(data['shares']),
        float(data['price'])
    )
    
    if success:
        return jsonify({
            'message': '出售成功',
            'transaction': {
                'id': result.id,
                'shares': result.shares,
                'price': float(result.price),
                'total_amount': float(result.total_amount)
            }
        })
    return jsonify({'message': result}), 400

@trading_bp.route('/holdings', methods=['GET'])
@login_required
def get_holdings():
    """获取持仓"""
    holdings = TradingService.get_user_holdings(current_user.id)
    return jsonify({
        'holdings': holdings,
        'total_value': sum(h['current_value'] for h in holdings)
    })

@trading_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """获取交易历史"""
    user_id = request.args.get('user_id', type=int)
    company_id = request.args.get('company_id', type=int)
    
    # 普通用户只能查看自己的交易历史
    if not current_user.is_admin and user_id != current_user.id:
        user_id = current_user.id
        
    transactions = TradingService.get_transaction_history(user_id, company_id)
    return jsonify({'transactions': transactions}) 