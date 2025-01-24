from flask import Blueprint, request, jsonify
from app.services.company_service import CompanyService
from app.utils.exceptions import CompanyError
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('company', __name__, url_prefix='/api/companies')
company_service = CompanyService()

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CompanyError as e:
            return jsonify({'error': str(e)}), e.status
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    return wrapper

@bp.route('/', methods=['POST'])
@jwt_required()
@handle_errors
def create_company():
    """创建新公司"""
    data = request.get_json()
    user_id = get_jwt_identity()
    company = company_service.create_company(
        name=data['name'],
        symbol=data['symbol'],
        description=data.get('description', ''),
        total_shares=data['total_shares'],
        owner_id=user_id
    )
    return jsonify(company.to_dict()), 201

@bp.route('/', methods=['GET'])
@handle_errors
def list_companies():
    """获取公司列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    companies = company_service.get_companies(page, per_page)
    return jsonify({
        'companies': [c.to_dict() for c in companies.items],
        'total': companies.total,
        'pages': companies.pages,
        'current_page': companies.page
    })

@bp.route('/<int:company_id>', methods=['GET'])
@handle_errors
def get_company(company_id):
    """获取公司详情"""
    company = company_service.get_company_by_id(company_id)
    return jsonify(company.to_dict())

@bp.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
@handle_errors
def update_company(company_id):
    """更新公司信息"""
    data = request.get_json()
    user_id = get_jwt_identity()
    company = company_service.update_company(
        company_id=company_id,
        owner_id=user_id,
        **data
    )
    return jsonify(company.to_dict())

@bp.route('/<int:company_id>/price', methods=['PUT'])
@jwt_required()
@handle_errors
def update_stock_price(company_id):
    """更新股票价格"""
    data = request.get_json()
    user_id = get_jwt_identity()
    company = company_service.update_stock_price(
        company_id=company_id,
        owner_id=user_id,
        new_price=data['price']
    )
    return jsonify(company.to_dict()) 