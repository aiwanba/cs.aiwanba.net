from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from apps.services.company_service import CompanyService
from apps.models.company import Company

company_bp = Blueprint('company', __name__)

@company_bp.route('/create', methods=['POST'])
@login_required
def create_company():
    """创建公司"""
    data = request.get_json()
    success, result = CompanyService.create_company(
        current_user,
        data['name'],
        data['description'],
        int(data['total_shares']),
        float(data['initial_price'])
    )
    
    if success:
        return jsonify({
            'message': '公司创建成功',
            'company': {
                'id': result.id,
                'name': result.name,
                'total_shares': result.total_shares,
                'current_price': float(result.current_price)
            }
        })
    return jsonify({'message': result}), 400

@company_bp.route('/market/data')
def get_market_data():
    """获取市场数据"""
    data = CompanyService.get_market_data()
    return jsonify(data)

@company_bp.route('/<int:company_id>')
def get_company(company_id):
    """获取公司详情"""
    company = Company.query.get_or_404(company_id)
    return jsonify({
        'id': company.id,
        'name': company.name,
        'description': company.description,
        'total_shares': company.total_shares,
        'available_shares': company.available_shares,
        'current_price': float(company.current_price),
        'market_value': company.market_value(),
        'owner': {
            'id': company.owner.id,
            'username': company.owner.username
        }
    }) 