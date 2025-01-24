from flask import Blueprint, request, jsonify
from services.bank_service import BankService
from models import db

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/accounts/create', methods=['POST'])
def create_account():
    """创建银行账户"""
    data = request.get_json()
    company_id = data.get('company_id')
    initial_balance = data.get('initial_balance', 0.0)
    
    if not company_id:
        return jsonify({'error': '缺少公司ID'}), 400
        
    try:
        account = BankService.create_account(company_id, initial_balance)
        return jsonify({
            'message': '账户创建成功',
            'account_id': account.id,
            'balance': account.balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/accounts/<int:account_id>/deposit', methods=['POST'])
def deposit(account_id):
    """存款接口"""
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description')
    
    if not amount or amount <= 0:
        return jsonify({'error': '无效的存款金额'}), 400
        
    try:
        if BankService.deposit(account_id, amount, description):
            return jsonify({'message': '存款成功'})
        return jsonify({'error': '账户不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/accounts/<int:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    """取款接口"""
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description')
    
    if not amount or amount <= 0:
        return jsonify({'error': '无效的取款金额'}), 400
        
    try:
        if BankService.withdraw(account_id, amount, description):
            return jsonify({'message': '取款成功'})
        return jsonify({'error': '余额不足或账户不存在'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/accounts/transfer', methods=['POST'])
def transfer():
    """转账接口"""
    data = request.get_json()
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    description = data.get('description')
    
    if not all([from_account_id, to_account_id, amount]) or amount <= 0:
        return jsonify({'error': '无效的转账参数'}), 400
        
    try:
        if BankService.transfer(from_account_id, to_account_id, amount, description):
            return jsonify({'message': '转账成功'})
        return jsonify({'error': '转账失败，请检查账户余额和账户状态'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 