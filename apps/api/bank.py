from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from apps.services.bank_service import BankService
from apps.models.bank import BankAccount

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/savings/create', methods=['POST'])
@login_required
def create_savings():
    """创建储蓄账户"""
    success, result = BankService.create_savings_account(current_user)
    if success:
        return jsonify({
            'message': '储蓄账户创建成功',
            'account': {
                'id': result.id,
                'balance': float(result.balance),
                'interest_rate': result.interest_rate
            }
        })
    return jsonify({'message': result}), 400

@bank_bp.route('/loan/create', methods=['POST'])
@login_required
def create_loan():
    """创建贷款账户"""
    data = request.get_json()
    success, result = BankService.create_loan_account(
        current_user,
        float(data['amount']),
        int(data['duration_days'])
    )
    if success:
        return jsonify({
            'message': '贷款申请成功',
            'account': {
                'id': result.id,
                'balance': float(result.balance),
                'interest_rate': result.interest_rate,
                'end_date': result.end_date.strftime('%Y-%m-%d')
            }
        })
    return jsonify({'message': result}), 400

@bank_bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    """存款"""
    data = request.get_json()
    success, result = BankService.deposit(
        int(data['account_id']),
        float(data['amount'])
    )
    if success:
        return jsonify({
            'message': '存款成功',
            'balance': float(result.balance)
        })
    return jsonify({'message': result}), 400

@bank_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    """取款"""
    data = request.get_json()
    success, result = BankService.withdraw(
        int(data['account_id']),
        float(data['amount'])
    )
    if success:
        return jsonify({
            'message': '取款成功',
            'balance': float(result.balance)
        })
    return jsonify({'message': result}), 400

@bank_bp.route('/loan/repay', methods=['POST'])
@login_required
def repay_loan():
    """还贷"""
    data = request.get_json()
    success, result = BankService.repay_loan(
        int(data['account_id']),
        float(data['amount'])
    )
    if success:
        return jsonify({
            'message': '还款成功',
            'remaining': float(result.balance)
        })
    return jsonify({'message': result}), 400

@bank_bp.route('/accounts')
@login_required
def get_accounts():
    """获取账户信息"""
    savings = BankAccount.query.filter_by(
        user_id=current_user.id,
        account_type='savings'
    ).first()
    
    loan = BankAccount.query.filter_by(
        user_id=current_user.id,
        account_type='loan',
        status='active'
    ).first()
    
    return jsonify({
        'savings': {
            'id': savings.id,
            'balance': float(savings.balance),
            'interest_rate': savings.interest_rate
        } if savings else None,
        'loan': {
            'id': loan.id,
            'balance': float(loan.balance),
            'interest_rate': loan.interest_rate,
            'end_date': loan.end_date.strftime('%Y-%m-%d')
        } if loan else None
    }) 