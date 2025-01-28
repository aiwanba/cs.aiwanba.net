from flask import Blueprint, request, g
from app.services.bank import BankService
from app.utils.response import success_response, error_response
from app.utils.auth import login_required, admin_required

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('', methods=['POST'])
@login_required
def create_bank():
    """创建银行"""
    data = request.get_json()
    name = data.get('name')
    capital = data.get('capital')
    deposit_rate = data.get('deposit_rate')
    loan_rate = data.get('loan_rate')
    
    # 验证必要字段
    if not all([name, capital, deposit_rate, loan_rate]):
        return error_response("请填写完整信息")
    
    # 验证数值范围
    try:
        capital = float(capital)
        deposit_rate = float(deposit_rate)
        loan_rate = float(loan_rate)
        
        if capital < 50000000:  # 最低注册资本5000万
            return error_response("注册资本不能低于5000万")
        if not (0 < deposit_rate < loan_rate):
            return error_response("存款利率必须大于0且小于贷款利率")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = BankService.create_bank(
        name, g.current_user.id, capital, deposit_rate, loan_rate
    )
    
    if success:
        return success_response(result.to_dict(), "银行创建成功")
    return error_response(result)

@bank_bp.route('', methods=['GET'])
def get_bank_list():
    """获取银行列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = BankService.get_bank_list(page, per_page)
    return success_response(result)

@bank_bp.route('/<int:bank_id>', methods=['GET'])
def get_bank_detail(bank_id):
    """获取银行详情"""
    success, result = BankService.get_bank_detail(bank_id)
    if success:
        return success_response(result)
    return error_response(result)

@bank_bp.route('/<int:bank_id>/deposit', methods=['POST'])
@login_required
def create_deposit(bank_id):
    """创建存款"""
    data = request.get_json()
    amount = data.get('amount')
    term = data.get('term')  # 存款期限(天)
    
    try:
        amount = float(amount)
        term = int(term)
        if amount <= 0:
            return error_response("存款金额必须大于0")
        if term <= 0:
            return error_response("存款期限必须大于0")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = BankService.create_deposit(
        bank_id, g.current_user.id, amount, term
    )
    
    if success:
        return success_response(result.to_dict(), "存款成功")
    return error_response(result)

@bank_bp.route('/<int:bank_id>/loan', methods=['POST'])
@login_required
def create_loan(bank_id):
    """创建贷款"""
    data = request.get_json()
    amount = data.get('amount')
    term = data.get('term')  # 贷款期限(天)
    collateral_type = data.get('collateral_type')
    collateral_id = data.get('collateral_id')
    
    try:
        amount = float(amount)
        term = int(term)
        if amount <= 0:
            return error_response("贷款金额必须大于0")
        if term <= 0:
            return error_response("贷款期限必须大于0")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = BankService.create_loan(
        bank_id, g.current_user.id, amount, term, collateral_type, collateral_id
    )
    
    if success:
        return success_response(result.to_dict(), "贷款成功")
    return error_response(result)

@bank_bp.route('/<int:bank_id>/rates', methods=['PUT'])
@login_required
def update_rates(bank_id):
    """更新利率"""
    data = request.get_json()
    deposit_rate = data.get('deposit_rate')
    loan_rate = data.get('loan_rate')
    
    if deposit_rate is None and loan_rate is None:
        return error_response("请至少提供一个利率")
    
    try:
        if deposit_rate is not None:
            deposit_rate = float(deposit_rate)
        if loan_rate is not None:
            loan_rate = float(loan_rate)
        if deposit_rate and loan_rate and deposit_rate >= loan_rate:
            return error_response("存款利率必须小于贷款利率")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = BankService.update_rates(bank_id, deposit_rate, loan_rate)
    if success:
        return success_response(result.to_dict(), "利率更新成功")
    return error_response(result) 