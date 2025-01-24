from flask import Blueprint, request, jsonify
from app.services.stock_service import StockService
from app.utils.exceptions import StockError
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('stock', __name__, url_prefix='/api/stocks')
stock_service = StockService()

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except StockError as e:
            return jsonify({'error': str(e)}), e.status
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

@bp.route('/buy', methods=['POST'])
@jwt_required()
@handle_errors
def buy_stock():
    """购买股票"""
    data = request.get_json()
    user_id = get_jwt_identity()
    transaction = stock_service.buy_stock(
        company_id=data['company_id'],
        user_id=user_id,
        quantity=data['quantity']
    )
    return jsonify(transaction.to_dict()), 201

@bp.route('/sell', methods=['POST'])
@jwt_required()
@handle_errors
def sell_stock():
    """卖出股票"""
    data = request.get_json()
    user_id = get_jwt_identity()
    transaction = stock_service.sell_stock(
        company_id=data['company_id'],
        user_id=user_id,
        quantity=data['quantity']
    )
    return jsonify(transaction.to_dict()), 201

@bp.route('/portfolio', methods=['GET'])
@jwt_required()
@handle_errors
def get_portfolio():
    """获取用户投资组合"""
    user_id = get_jwt_identity()
    portfolio = stock_service.get_user_portfolio(user_id)
    return jsonify(portfolio)

@bp.route('/transactions', methods=['GET'])
@jwt_required()
@handle_errors
def get_transactions():
    """获取交易历史"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transactions = stock_service.get_user_transactions(user_id, page, per_page)
    return jsonify({
        'transactions': [t.to_dict() for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': transactions.page
    })

@bp.route('/market-data', methods=['GET'])
@handle_errors
def get_market_data():
    """获取市场数据"""
    return jsonify(stock_service.get_market_data()) 