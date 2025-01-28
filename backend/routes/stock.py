from flask import jsonify, request, g
from . import stock_bp
from services.stock import StockService
from app import db
from models.company import Company
from models.stock import Stock
from models.order import Order
from flask import current_app
from middlewares.auth import login_required
from services.matching_engine import MatchingEngine

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
@login_required
def execute_trade():
    """执行交易"""
    try:
        data = request.get_json()
        user_id = g.user_id
        
        # 验证必要字段
        required_fields = ['company_id', 'type', 'price', 'quantity']
        if not all(k in data for k in required_fields):
            return jsonify({'message': '缺少必要字段'}), 400
            
        company_id = data['company_id']
        trade_type = data['type']
        price = float(data['price'])
        quantity = int(data['quantity'])
        
        # 根据交易类型设置买卖方
        if trade_type == 'buy':
            buyer_id = user_id
            seller_id = None  # 由撮合引擎匹配卖方
        else:  # sell
            seller_id = user_id
            buyer_id = None  # 由撮合引擎匹配买方
            
        # 创建订单
        order = Order(
            company_id=company_id,
            user_id=user_id,
            order_type=trade_type,
            amount=quantity,
            price=price,
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 尝试撮合
        MatchingEngine.try_match(company_id)
        
        return jsonify({
            'message': '交易提交成功',
            'data': {
                'order_id': order.id,
                'status': order.status
            }
        })
        
    except ValueError as e:
        current_app.logger.error(f"交易参数错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"交易提交失败: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '交易提交失败'}), 500

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

@stock_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """撤销订单"""
    try:
        user_id = g.user_id
        order = Order.query.get_or_404(order_id)
        
        # 验证订单所有者
        if order.user_id != user_id:
            return jsonify({'message': '无权操作此订单'}), 403
            
        # 验证订单状态
        if order.status != 'pending':
            return jsonify({'message': '只能撤销待处理的订单'}), 400
            
        # 更新订单状态
        order.status = 'cancelled'
        
        # 如果是卖单，解冻股票
        if order.order_type == 'sell':
            frozen_stock = Stock.query.filter_by(
                company_id=order.company_id,
                holder_id=user_id,
                is_frozen=True
            ).first()
            
            if frozen_stock:
                # 创建或更新可用持仓
                available_stock = Stock.query.filter_by(
                    company_id=order.company_id,
                    holder_id=user_id,
                    is_frozen=False
                ).first()
                
                if not available_stock:
                    available_stock = Stock(
                        company_id=order.company_id,
                        holder_id=user_id,
                        amount=0,
                        is_frozen=False
                    )
                    db.session.add(available_stock)
                    
                available_stock.amount += frozen_stock.amount
                db.session.delete(frozen_stock)
                
        db.session.commit()
        
        return jsonify({
            'message': '订单已撤销',
            'data': {
                'order_id': order.id,
                'status': order.status
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"撤销订单失败: {str(e)}")
        db.session.rollback()
        return jsonify({'message': '撤销订单失败'}), 500

# 缺少以下接口：
# 1. 获取市场行情
# 2. 获取个人持仓
# 3. 获取订单列表 