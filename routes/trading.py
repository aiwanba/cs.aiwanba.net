from flask import Blueprint, request, jsonify
from models.transaction import Transaction, OrderBook
from models.company import Company
from models.shareholder import Shareholder
from routes.notification import send_notification
from app import db

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/api/trade/<int:company_id>', methods=['POST'])
def place_order(company_id):
    try:
        data = request.get_json()
        required_fields = ['order_type', 'shares']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        company = Company.query.get_or_404(company_id)
        user_id = request.user_id  # 假设通过认证中间件设置
        
        # 创建订单
        order = OrderBook(
            company_id=company_id,
            user_id=user_id,
            order_type=data['order_type'],
            shares=data['shares']
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 尝试撮合交易
        match_orders(company_id)
        
        # 添加大单提醒
        if data['shares'] > company.total_shares * 0.01:  # 超过1%的大单
            send_notification(
                'transaction',
                'info',
                '大额交易提醒',
                f'公司{company.name}出现大额{data["order_type"]}单，数量{data["shares"]}股',
                company_id
            )
        
        return jsonify({
            'status': 'success',
            'message': 'Order placed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def match_orders(company_id):
    """撮合交易"""
    # 获取所有待处理的买单和卖单
    buy_orders = OrderBook.query.filter_by(
        company_id=company_id,
        order_type='buy',
        status='pending'
    ).order_by(OrderBook.created_at).all()
    
    sell_orders = OrderBook.query.filter_by(
        company_id=company_id,
        order_type='sell',
        status='pending'
    ).order_by(OrderBook.created_at).all()
    
    company = Company.query.get(company_id)
    
    for buy_order in buy_orders:
        for sell_order in sell_orders:
            if sell_order.shares == 0:
                continue
                
            # 确定成交数量
            trade_shares = min(buy_order.shares, sell_order.shares)
            if trade_shares <= 0:
                continue
                
            # 创建交易记录
            transaction = Transaction(
                company_id=company_id,
                seller_id=sell_order.user_id,
                buyer_id=buy_order.user_id,
                shares=trade_shares,
                price=company.stock_price  # 使用当前股价
            )
            
            # 更新订单状态
            buy_order.shares -= trade_shares
            sell_order.shares -= trade_shares
            
            # 更新股东持股记录
            update_shareholding(company_id, sell_order.user_id, -trade_shares)
            update_shareholding(company_id, buy_order.user_id, trade_shares)
            
            db.session.add(transaction)
            
            # 如果订单完成，标记状态
            if buy_order.shares == 0:
                buy_order.status = 'completed'
            if sell_order.shares == 0:
                sell_order.status = 'completed'
    
    db.session.commit()

def update_shareholding(company_id, user_id, shares_change):
    """更新股东持股数量"""
    shareholder = Shareholder.query.filter_by(
        company_id=company_id,
        user_id=user_id
    ).first()
    
    if shareholder:
        shareholder.shares += shares_change
        if shareholder.shares < 0:
            raise ValueError('Insufficient shares')
    else:
        if shares_change > 0:
            shareholder = Shareholder(
                company_id=company_id,
                user_id=user_id,
                shares=shares_change
            )
            db.session.add(shareholder)

@trading_bp.route('/api/orderbook/<int:company_id>', methods=['GET'])
def get_orderbook(company_id):
    """获取当前订单簿"""
    buy_orders = OrderBook.query.filter_by(
        company_id=company_id,
        order_type='buy',
        status='pending'
    ).all()
    
    sell_orders = OrderBook.query.filter_by(
        company_id=company_id,
        order_type='sell',
        status='pending'
    ).all()
    
    return jsonify({
        'buy_orders': [{'shares': o.shares, 'created_at': o.created_at.isoformat()} for o in buy_orders],
        'sell_orders': [{'shares': o.shares, 'created_at': o.created_at.isoformat()} for o in sell_orders]
    }) 