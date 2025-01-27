from flask import jsonify, request
from . import bank_bp
from services.bank import BankService
from app import db
from services.interest import InterestService

@bank_bp.route('/create', methods=['POST'])
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
        return jsonify({'error': '创建银行失败'}), 500

@bank_bp.route('/account/open', methods=['POST'])
def open_account():
    """开户"""
    data = request.get_json()
    
    required_fields = ['bank_id', 'user_id']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        account = BankService.open_account(
            bank_id=data['bank_id'],
            user_id=data['user_id']
        )
        
        return jsonify({
            'message': '开户成功',
            'account': {
                'id': account.id,
                'balance': float(account.balance),
                'interest_rate': account.interest_rate
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '开户失败'}), 500

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