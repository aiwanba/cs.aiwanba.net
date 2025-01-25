from flask import Blueprint, request, jsonify, session, render_template, abort, redirect, url_for
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

@company_bp.route('/api/info/<int:company_id>')
def company_info_api(company_id):
    """获取公司信息API"""
    info = CompanyService.get_company_info(company_id)
    if info:
        return jsonify({"success": True, "data": info})
    return jsonify({"success": False, "message": "公司不存在"})

@company_bp.route('/list')
def company_list():
    """获取公司列表"""
    companies = CompanyService.get_company_list()
    return jsonify({"success": True, "data": companies})

@company_bp.route('/info/<int:company_id>')
def company_info_page(company_id):
    """公司详情页面"""
    info = CompanyService.get_company_info(company_id)
    if not info:
        abort(404)
    return render_template('company/info.html', company=info)

@company_bp.route('/<int:company_id>/transactions')
def company_transactions(company_id):
    """获取公司交易历史"""
    transactions = CompanyService.get_company_transactions(company_id)
    return jsonify({"success": True, "data": transactions})

@company_bp.route('/create')
def create_page():
    """创建公司页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('company/create.html') 