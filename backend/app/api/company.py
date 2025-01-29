from flask import Blueprint, request, g
from app.services.company import CompanyService
from app.utils.response import success_response, error_response
from app.utils.auth import login_required, admin_required

company_bp = Blueprint('company', __name__)

@company_bp.route('', methods=['POST'])
@login_required
def create_company():
    """创建公司"""
    data = request.get_json()
    name = data.get('name')
    stock_code = data.get('stock_code')
    industry = data.get('industry')
    total_shares = data.get('total_shares')
    initial_price = data.get('initial_price')
    
    # 验证必要字段
    if not all([name, stock_code, industry, total_shares, initial_price]):
        return error_response("请填写完整信息")
    
    # 验证数值范围
    try:
        total_shares = int(total_shares)
        initial_price = float(initial_price)
        if not (100000 <= total_shares <= 1000000):
            return error_response("总股本必须在10万到100万股之间")
        if not (10 <= initial_price <= 100):
            return error_response("发行价必须在10到100元之间")
    except ValueError:
        return error_response("数值格式错误")
    
    success, result = CompanyService.create_company(
        name, stock_code, industry, total_shares, initial_price, g.current_user.id
    )
    
    if success:
        return success_response(result.to_dict(), "公司创建成功")
    return error_response(result)

@company_bp.route('', methods=['GET'])
def get_company_list():
    """获取公司列表"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    industry = request.args.get('industry')
    
    result = CompanyService.get_company_list(page, per_page, industry)
    return success_response(result)

@company_bp.route('/<int:company_id>', methods=['GET'])
def get_company_detail(company_id):
    """获取公司详情"""
    success, result = CompanyService.get_company_detail(company_id)
    if success:
        return success_response(result)
    return error_response(result)

@company_bp.route('/<int:company_id>/status', methods=['PUT'])
@admin_required
def update_company_status(company_id):
    """更新公司状态（管理员专用）"""
    data = request.get_json()
    status = data.get('status')
    
    if status not in [0, 1, 2]:
        return error_response("无效的状态值")
    
    success, result = CompanyService.update_company_status(company_id, status)
    if success:
        return success_response(result.to_dict(), "状态更新成功")
    return error_response(result)

@company_bp.route('/<int:company_id>', methods=['PUT'])
@login_required
def update_company(company_id):
    """更新公司信息"""
    data = request.get_json()
    name = data.get('name')
    industry = data.get('industry')
    cash_balance = data.get('cash_balance')
    
    # 验证必要字段
    if not any([name, industry, cash_balance]):
        return error_response("至少需要提供一个更新字段")
    
    success, result = CompanyService.update_company(company_id, data)
    if success:
        return success_response(result.to_dict(), "公司信息更新成功")
    return error_response(result) 