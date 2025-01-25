from flask import Blueprint, request, jsonify, session
from services.trading import TradingService

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/buy', methods=['POST'])
def buy_stock():
    """买入股票接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    company_id = data.get('company_id')
    shares = data.get('shares')
    price = data.get('price')
    
    if not all([company_id, shares, price]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    try:
        shares = int(shares)
        price = float(price)
        if shares <= 0 or price <= 0:
            return jsonify({"success": False, "message": "数量和价格必须大于0"})
    except ValueError:
        return jsonify({"success": False, "message": "请输入有效的数字"})
    
    success, message = TradingService.buy_stock(
        session['user_id'], company_id, shares, price
    )
    return jsonify({"success": success, "message": message})

@trading_bp.route('/sell', methods=['POST'])
def sell_stock():
    """卖出股票接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    company_id = data.get('company_id')
    shares = data.get('shares')
    price = data.get('price')
    
    if not all([company_id, shares, price]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    try:
        shares = int(shares)
        price = float(price)
        if shares <= 0 or price <= 0:
            return jsonify({"success": False, "message": "数量和价格必须大于0"})
    except ValueError:
        return jsonify({"success": False, "message": "请输入有效的数字"})
    
    success, message = TradingService.sell_stock(
        session['user_id'], company_id, shares, price
    )
    return jsonify({"success": success, "message": message})

@trading_bp.route('/holdings')
def get_holdings():
    """获取持股信息接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    holdings = TradingService.get_stock_holdings(session['user_id'])
    return jsonify({"success": True, "data": holdings}) 