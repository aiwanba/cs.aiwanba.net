from flask import jsonify, request, g
from . import stock_bp
from services.stock import StockService
from app import db
from models.company import Company
from models.stock import Stock
from models.order import Order
from flask import current_app
from middlewares.auth import login_required

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

@stock_bp.route('/market', methods=['GET'])
@login_required
def get_market_data():
    """获取市场行情"""
    try:
        # 获取公司ID参数
        company_id = request.args.get('company_id')
        
        if company_id:
            # 获取指定公司行情
            company = Company.query.get_or_404(company_id)
            return jsonify({
                'message': '获取成功',
                'data': {
                    'company': company.to_dict(),
                    'current_price': float(company.current_price),
                    'total_shares': company.total_shares,
                    'market_value': float(company.current_price * company.total_shares)
                }
            })
        else:
            # 获取所有公司行情
            companies = Company.query.all()
            return jsonify({
                'message': '获取成功',
                'data': [company.to_dict() for company in companies]
            })
            
    except Exception as e:
        current_app.logger.error(f"获取市场行情失败: {str(e)}")
        return jsonify({'message': '获取市场行情失败'}), 500

@stock_bp.route('/positions', methods=['GET'])
@login_required
def get_positions():
    """获取个人持仓"""
    try:
        # 从token中获取用户ID
        user_id = g.user_id  # 需要添加认证中间件
        
        # 获取用户所有持仓
        stocks = Stock.query.filter_by(
            holder_id=user_id,
            is_frozen=False
        ).all()
        
        positions = []
        for stock in stocks:
            company = Company.query.get(stock.company_id)
            if company:
                positions.append({
                    'company_id': company.id,
                    'company_name': company.name,
                    'amount': stock.amount,
                    'current_price': float(company.current_price),
                    'market_value': float(company.current_price * stock.amount)
                })
        
        return jsonify({
            'message': '获取成功',
            'data': positions
        })
        
    except Exception as e:
        current_app.logger.error(f"获取持仓数据失败: {str(e)}")
        return jsonify({'message': '获取持仓数据失败'}), 500

@stock_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """获取订单列表"""
    try:
        user_id = g.user_id  # 需要添加认证中间件
        
        # 获取用户所有订单
        orders = Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).all()
        
        order_list = []
        for order in orders:
            company = Company.query.get(order.company_id)
            order_list.append({
                'id': order.id,
                'company_name': company.name if company else 'Unknown',
                'order_type': order.order_type,
                'amount': order.amount,
                'price': float(order.price),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })
            
        return jsonify({
            'message': '获取成功',
            'data': order_list
        })
        
    except Exception as e:
        current_app.logger.error(f"获取订单数据失败: {str(e)}")
        return jsonify({'message': '获取订单数据失败'}), 500

# 缺少以下接口：
# 1. 获取市场行情
# 2. 获取个人持仓
# 3. 获取订单列表 