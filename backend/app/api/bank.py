from flask import Blueprint, request, g
from app.services.bank import BankService
from app.utils.response import success_response, error_response
from app.utils.auth import login_required, admin_required
from flask_jwt_extended import jwt_required, get_jwt_identity

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
    reserve_ratio = data.get('reserve_ratio', 10.00)  # 默认10%
    
    # 验证必要字段
    if not all([name, capital, deposit_rate, loan_rate]):
        return error_response("请填写完整信息")
    
    # 验证数值范围
    try:
        capital = float(capital)
        deposit_rate = float(deposit_rate)
        loan_rate = float(loan_rate)
        reserve_ratio = float(reserve_ratio)
        
        if capital < 50000000:  # 最低注册资本5000万
            return error_response("注册资本不能低于5000万")
        if not (0 < deposit_rate < loan_rate):
            return error_response("存款利率必须大于0且小于贷款利率")
        if not (0 < reserve_ratio <= 100):
            return error_response("准备金率必须在0-100%之间")
            
        # 检查用户现金是否足够
        if g.current_user.cash < capital:
            return error_response("现金余额不足")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = BankService.create_bank(
        name=name,
        owner_id=g.current_user.id,
        capital=capital,
        deposit_rate=deposit_rate,
        loan_rate=loan_rate,
        reserve_ratio=reserve_ratio
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
@jwt_required()
def create_loan(bank_id):
    """创建贷款"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    amount = data.get('amount')
    term = data.get('term')
    collateral_type = data.get('collateral_type')
    collateral_id = data.get('collateral_id')
    
    success, result = BankService.create_loan(
        bank_id=bank_id,
        user_id=user_id,
        amount=amount,
        term=term,
        collateral_type=collateral_type,
        collateral_id=collateral_id
    )
    
    if not success:
        return error_response(result)
    
    return success_response(result)

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