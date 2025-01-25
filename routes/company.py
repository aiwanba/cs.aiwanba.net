from flask import Blueprint, request, jsonify, session
from services.company import CompanyService

company_bp = Blueprint('company', __name__)

@company_bp.route('/create', methods=['POST'])
def create_company():
    """创建公司接口"""
    # 检查用户是否登录
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    total_shares = data.get('total_shares')
    initial_price = data.get('initial_price')
    
    if not all([name, description, total_shares, initial_price]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    try:
        total_shares = int(total_shares)
        initial_price = float(initial_price)
        if total_shares <= 0 or initial_price <= 0:
            return jsonify({"success": False, "message": "股份数量和价格必须大于0"})
    except ValueError:
        return jsonify({"success": False, "message": "请输入有效的数字"})
    
    success, result = CompanyService.create_company(
        name, description, total_shares, initial_price, session['user_id']
    )
    
    if success:
        return jsonify({
            "success": True,
            "message": "公司创建成功",
            "data": CompanyService.get_company_info(result.id)
        })
    return jsonify({"success": False, "message": result})

@company_bp.route('/info/<int:company_id>')
def company_info(company_id):
    """获取公司信息接口"""
    info = CompanyService.get_company_info(company_id)
    if info:
        return jsonify({"success": True, "data": info})
    return jsonify({"success": False, "message": "公司不存在"}) 