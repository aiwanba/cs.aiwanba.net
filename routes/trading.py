from flask import Blueprint, request, jsonify, session
from services.trading import TradingService
from functools import wraps

trading_bp = Blueprint('trading', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "请先登录"}), 401
        return f(*args, **kwargs)
    return decorated_function

@trading_bp.route('/buy', methods=['POST'])
@login_required
def buy_stock():
    """买入股票接口"""
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
@login_required
def sell_stock():
    """卖出股票接口"""
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
@login_required
def get_holdings():
    """获取持股信息接口"""
    holdings = TradingService.get_stock_holdings(session['user_id'])
    return jsonify({"success": True, "data": holdings}) 