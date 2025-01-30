from flask import Blueprint, request, g
from app.services.trade import TradeService
from app.utils.response import success_response, error_response
from app.utils.auth import login_required

trade_bp = Blueprint('trade', __name__)

@trade_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """创建交易订单"""
    data = request.get_json()
    company_id = data.get('company_id')
    order_type = data.get('order_type')  # 1-买入，2-卖出
    price_type = data.get('price_type')  # 1-市价，2-限价
    price = data.get('price')
    quantity = data.get('quantity')
    
    # 验证必要字段
    if not all([company_id, order_type, price_type, quantity]):
        return error_response("请填写完整信息")
    
    # 验证数值
    try:
        company_id = int(company_id)
        order_type = int(order_type)
        price_type = int(price_type)
        quantity = int(quantity)
        
        if order_type not in [1, 2]:
            return error_response("无效的订单类型")
        if price_type not in [1, 2]:
            return error_response("无效的价格类型")
        
        if price_type == 2:  # 限价单必须指定价格
            if not price:
                return error_response("请指定交易价格")
            price = float(price)
            if price <= 0:
                return error_response("价格必须大于0")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = TradeService.create_order(
        company_id, g.current_user.id, order_type, price_type, price, quantity
    )
    
    if success:
        return success_response(result.to_dict(), "订单创建成功")
    return error_response(result)

@trade_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@login_required
def cancel_order(order_id):
    """撤销订单"""
    success, result = TradeService.cancel_order(order_id, g.current_user.id)
    if success:
        return success_response(result.to_dict(), "订单已撤销")
    return error_response(result)

@trade_bp.route('/orders', methods=['GET'])
@login_required
def get_order_list():
    """获取订单列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    company_id = request.args.get('company_id')
    status = request.args.get('status')
    
    # 默认只显示当前用户的订单
    result = TradeService.get_order_list(
        user_id=g.current_user.id,
        company_id=company_id,
        status=status,
        page=page,
        per_page=per_page
    )
    return success_response(result)

@trade_bp.route('/trades', methods=['GET'])
def get_trade_list():
    """获取成交记录"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    company_id = request.args.get('company_id')
    
    result = TradeService.get_trade_list(company_id, page, per_page)
    return success_response(result) 