from flask import jsonify, request, g, current_app
from . import bank_bp
from services.bank import BankService
from app import db
from services.interest import InterestService
from middlewares.auth import login_required
from models import Bank, BankAccount, BankTransaction

@bank_bp.route('/create', methods=['POST'])
@login_required
def create_bank():
    """创建银行"""
    data = request.get_json()
    
    required_fields = ['owner_id', 'name']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        bank = BankService.create_bank(
            owner_id=data['owner_id'],
            name=data['name']
        )
        
        return jsonify({
            'message': '银行创建成功',
            'bank': {
                'id': bank.id,
                'name': bank.name,
                'total_assets': float(bank.total_assets),
                'reserve_ratio': bank.reserve_ratio
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"创建银行失败: {str(e)}")
        return jsonify({'error': '创建银行失败'}), 500

@bank_bp.route('/banks', methods=['GET'])
@login_required
def get_banks():
    """获取可用银行列表"""
    try:
        banks = Bank.query.all()
        return jsonify({
            'message': '获取成功',
            'data': [{
                'id': bank.id,
                'name': bank.name,
                'reserve_ratio': bank.reserve_ratio,
                'interest_rate': 0.03  # 基准利率
            } for bank in banks]
        })
    except Exception as e:
        current_app.logger.error(f"获取银行列表失败: {str(e)}")
        return jsonify({'message': '获取银行列表失败'}), 500

@bank_bp.route('/account/open', methods=['POST'])
@login_required
def open_account():
    """开户"""
    try:
        data = request.get_json()
        
        # 从认证中间件获取用户ID
        user_id = g.user_id
        
        # 验证银行ID
        bank_id = data.get('bank_id')
        if not bank_id:
            return jsonify({'message': '请选择开户银行'}), 400
            
        account = BankService.open_account(
            bank_id=bank_id,
            user_id=user_id
        )
        
        return jsonify({
            'message': '开户成功',
            'data': {
                'id': account.id,
                'account_number': account.account_number,
                'balance': float(account.balance),
                'interest_rate': account.interest_rate
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"开户失败: {str(e)}")
        return jsonify({'message': '开户失败'}), 500

@bank_bp.route('/account/deposit', methods=['POST'])
def deposit():
    """存款"""
    data = request.get_json()
    
    required_fields = ['account_id', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        transaction = BankService.deposit(
            account_id=data['account_id'],
            amount=data['amount']
        )
        
        return jsonify({
            'message': '存款成功',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'created_at': transaction.created_at.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '存款失败'}), 500

@bank_bp.route('/account/withdraw', methods=['POST'])
def withdraw():
    """取款"""
    data = request.get_json()
    
    required_fields = ['account_id', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        transaction = BankService.withdraw(
            account_id=data['account_id'],
            amount=data['amount']
        )
        
        return jsonify({
            'message': '取款成功',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'created_at': transaction.created_at.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '取款失败'}), 500

@bank_bp.route('/loan/apply', methods=['POST'])
def apply_loan():
    """申请贷款"""
    data = request.get_json()
    
    required_fields = ['account_id', 'amount', 'duration_months']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        loan_account, transaction = BankService.apply_loan(
            account_id=data['account_id'],
            amount=data['amount'],
            duration_months=data['duration_months']
        )
        
        return jsonify({
            'message': '贷款申请成功',
            'loan_account': {
                'id': loan_account.id,
                'balance': float(loan_account.balance),
                'interest_rate': loan_account.interest_rate,
                'duration_months': loan_account.loan_duration
            },
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'created_at': transaction.created_at.isoformat()
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '贷款申请失败'}), 500

@bank_bp.route('/loan/repay', methods=['POST'])
def repay_loan():
    """还款"""
    data = request.get_json()
    
    required_fields = ['loan_account_id', 'amount']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        transaction = BankService.repay_loan(
            loan_account_id=data['loan_account_id'],
            amount=data['amount']
        )
        
        return jsonify({
            'message': '还款成功',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'created_at': transaction.created_at.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '还款失败'}), 500

@bank_bp.route('/interest/rate', methods=['POST'])
def adjust_interest_rate():
    """调整利率"""
    data = request.get_json()
    
    required_fields = ['bank_id', 'account_type', 'new_rate']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        InterestService.adjust_interest_rate(
            bank_id=data['bank_id'],
            account_type=data['account_type'],
            new_rate=data['new_rate']
        )
        
        return jsonify({
            'message': '利率调整成功',
            'new_rate': data['new_rate']
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '利率调整失败'}), 500

@bank_bp.route('/account', methods=['GET'])
@login_required
def get_account():
    """获取账户信息"""
    try:
        user_id = g.user_id
        account = BankAccount.query.filter_by(user_id=user_id).first()
        
        if not account:
            return jsonify({
                'message': '未开立账户',
                'account': None
            })
            
        return jsonify({
            'message': '获取成功',
            'account': {
                'id': account.id,
                'account_number': account.account_number,
                'balance': float(account.balance),
                'interest_rate': account.interest_rate
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取账户信息失败: {str(e)}")
        return jsonify({'message': '获取账户信息失败'}), 500

@bank_bp.route('/transactions/recent', methods=['GET'])
@login_required
def get_recent_transactions():
    """获取最近交易记录"""
    try:
        user_id = g.user_id
        account = BankAccount.query.filter_by(user_id=user_id).first()
        
        if not account:
            return jsonify({
                'message': '未开立账户',
                'transactions': []
            })
            
        transactions = BankTransaction.query.filter_by(
            account_id=account.id
        ).order_by(
            BankTransaction.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'message': '获取成功',
            'transactions': [{
                'id': tx.id,
                'type': tx.transaction_type,
                'amount': float(tx.amount),
                'created_at': tx.created_at.isoformat()
            } for tx in transactions]
        })
        
    except Exception as e:
        current_app.logger.error(f"获取交易记录失败: {str(e)}")
        return jsonify({'message': '获取交易记录失败'}), 500 