from flask import jsonify
from . import dashboard_bp
from models import User, Stock, Company, BankAccount
from extensions import db

@dashboard_bp.route('/summary', methods=['GET'])
def get_summary():
    """获取用户仪表盘数据"""
    # TODO: 从 token 中获取用户 ID
    user_id = 1  # 临时写死，后面改为从 token 获取
    
    try:
        # 获取用户信息
        user = User.query.get_or_404(user_id)
        
        # 获取持仓信息
        stocks = Stock.query.filter_by(holder_id=user_id, is_frozen=False).all()
        stock_value = sum(
            stock.amount * Company.query.get(stock.company_id).current_price 
            for stock in stocks
        )
        
        # 获取银行账户信息
        bank_accounts = BankAccount.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'userAssets': {
                'cash': float(user.balance),
                'stockValue': float(stock_value),
                'total': float(user.balance + stock_value)
            },
            'stockSummary': {
                'companyCount': len(set(stock.company_id for stock in stocks)),
                'totalShares': sum(stock.amount for stock in stocks),
                'profit': 0  # TODO: 计算浮动盈亏
            },
            'bankSummary': {
                'savings': sum(float(acc.balance) for acc in bank_accounts),
                'loans': 0,  # TODO: 实现贷款统计
                'netAssets': sum(float(acc.balance) for acc in bank_accounts)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 