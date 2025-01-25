from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from services.bank import BankService

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/')
def bank_page():
    """银行主页"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
        
    # 获取用户银行账户
    account = BankService.get_account(session['user_id'])
    if not account:
        # 如果没有账户，自动创建
        success, account = BankService.create_account(session['user_id'])
        if not success:
            return render_template('bank/error.html', message=account)
            
    # 获取用户贷款
    loans = BankService.get_user_loans(session['user_id'])
    # 获取最近交易记录
    transactions = BankService.get_recent_transactions(account.id)
    
    return render_template('bank/index.html', 
                         account=account,
                         loans=loans,
                         transactions=transactions)

@bank_bp.route('/deposit', methods=['POST'])
def deposit():
    """存款接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    account_id = data.get('account_id')
    amount = data.get('amount')
    
    if not all([account_id, amount]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = BankService.deposit(account_id, amount)
    if success:
        return jsonify({
            "success": True,
            "message": "存款成功",
            "data": {
                "balance": float(result.balance_after)
            }
        })
    return jsonify({"success": False, "message": result})

@bank_bp.route('/withdraw', methods=['POST'])
def withdraw():
    """取款接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    account_id = data.get('account_id')
    amount = data.get('amount')
    
    if not all([account_id, amount]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = BankService.withdraw(account_id, amount)
    if success:
        return jsonify({
            "success": True,
            "message": "取款成功",
            "data": {
                "balance": float(result.balance_after)
            }
        })
    return jsonify({"success": False, "message": result})

@bank_bp.route('/loan/apply', methods=['POST'])
def apply_loan():
    """申请贷款接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    amount = data.get('amount')
    term_months = data.get('term_months')
    
    if not all([amount, term_months]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = BankService.apply_loan(session['user_id'], amount, term_months)
    if success:
        return jsonify({
            "success": True,
            "message": "贷款申请成功",
            "data": {
                "loan_id": result.id,
                "amount": float(result.amount),
                "interest_rate": float(result.interest_rate)
            }
        })
    return jsonify({"success": False, "message": result})

@bank_bp.route('/loan/repay', methods=['POST'])
def repay_loan():
    """还款接口"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    loan_id = data.get('loan_id')
    amount = data.get('amount')
    
    if not all([loan_id, amount]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = BankService.repay_loan(loan_id, amount)
    if success:
        return jsonify({
            "success": True,
            "message": "还款成功",
            "data": {
                "remaining": float(result.remaining_amount)
            }
        })
    return jsonify({"success": False, "message": result}) 