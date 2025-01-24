from flask import Blueprint, request, jsonify
from app.services.bank_service import BankService
from app.utils.exceptions import BankError
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('bank', __name__, url_prefix='/api/bank')
bank_service = BankService()

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BankError as e:
            return jsonify({'error': str(e)}), e.status
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

@bp.route('/account', methods=['POST'])
@jwt_required()
@handle_errors
def create_account():
    """创建银行账户"""
    user_id = get_jwt_identity()
    data = request.get_json()
    account = bank_service.create_account(
        user_id=user_id,
        bank_id=data['bank_id']
    )
    return jsonify(account.to_dict()), 201

@bp.route('/deposit', methods=['POST'])
@jwt_required()
@handle_errors
def deposit():
    """存款"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result = bank_service.deposit(
        user_id=user_id,
        amount=data['amount']
    )
    return jsonify(result)

@bp.route('/withdraw', methods=['POST'])
@jwt_required()
@handle_errors
def withdraw():
    """取款"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result = bank_service.withdraw(
        user_id=user_id,
        amount=data['amount']
    )
    return jsonify(result)

@bp.route('/loan/apply', methods=['POST'])
@jwt_required()
@handle_errors
def apply_loan():
    """申请贷款"""
    user_id = get_jwt_identity()
    data = request.get_json()
    loan = bank_service.apply_loan(
        user_id=user_id,
        amount=data['amount'],
        term_months=data['term_months']
    )
    return jsonify(loan.to_dict()), 201

@bp.route('/loan/<int:loan_id>/repay', methods=['POST'])
@jwt_required()
@handle_errors
def repay_loan(loan_id):
    """还款"""
    user_id = get_jwt_identity()
    data = request.get_json()
    result = bank_service.repay_loan(
        loan_id=loan_id,
        user_id=user_id,
        amount=data['amount']
    )
    return jsonify(result)

@bp.route('/account/balance', methods=['GET'])
@jwt_required()
@handle_errors
def get_balance():
    """查询账户余额"""
    user_id = get_jwt_identity()
    balance = bank_service.get_account_balance(user_id)
    return jsonify(balance)

@bp.route('/loans', methods=['GET'])
@jwt_required()
@handle_errors
def get_loans():
    """获取贷款列表"""
    user_id = get_jwt_identity()
    loans = bank_service.get_user_loans(user_id)
    return jsonify(loans)

@bp.route('/interest-rate', methods=['GET'])
@handle_errors
def get_interest_rate():
    """获取当前利率"""
    return jsonify(bank_service.get_current_interest_rate()) 