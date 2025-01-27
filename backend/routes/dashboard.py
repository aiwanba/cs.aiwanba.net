from flask import jsonify
from . import dashboard_bp
from models import User, Stock, Company, BankAccount
from extensions import db
import logging

@dashboard_bp.route('/summary', methods=['GET'])
def get_summary():
    """获取用户仪表盘数据"""
    try:
        # TODO: 从 token 中获取用户 ID
        user_id = 1
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User not found: {user_id}")
            return jsonify({'error': '用户不存在'}), 404
            
        logging.info(f"Found user: {user.username}")
        
        # 获取持仓信息
        try:
            stocks = Stock.query.filter_by(holder_id=user_id, is_frozen=False).all()
            logging.info(f"Found {len(stocks)} stocks")
        except Exception as e:
            logging.error(f"Error getting stocks: {str(e)}")
            return jsonify({'error': '获取持仓信息失败'}), 500
        
        # 计算股票价值
        stock_value = 0
        try:
            for stock in stocks:
                company = Company.query.get(stock.company_id)
                if company:
                    stock_value += stock.amount * company.current_price
        except Exception as e:
            logging.error(f"Error calculating stock value: {str(e)}")
            return jsonify({'error': '计算股票价值失败'}), 500
        
        # 获取银行账户信息
        try:
            bank_accounts = BankAccount.query.filter_by(user_id=user_id).all()
            logging.info(f"Found {len(bank_accounts)} bank accounts")
            total_savings = sum(float(acc.balance) for acc in bank_accounts) if bank_accounts else 0
        except Exception as e:
            logging.error(f"Error getting bank accounts: {str(e)}")
            return jsonify({'error': '获取银行账户信息失败'}), 500
        
        return jsonify({
            'userAssets': {
                'cash': float(user.balance),
                'stockValue': float(stock_value),
                'total': float(user.balance + stock_value)
            },
            'stockSummary': {
                'companyCount': len(set(stock.company_id for stock in stocks)),
                'totalShares': sum(stock.amount for stock in stocks),
                'profit': 0
            },
            'bankSummary': {
                'savings': total_savings,
                'loans': 0,
                'netAssets': total_savings
            }
        })
        
    except Exception as e:
        logging.error(f"Error in dashboard summary: {str(e)}")
        return jsonify({'error': str(e)}), 500 