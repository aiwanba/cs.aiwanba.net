from flask import jsonify, request, current_app
from . import company_bp
from services.company import CompanyService
from app import db
from models import Company

@company_bp.route('/create', methods=['POST'])
def create_company():
    """创建公司"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['owner_id', 'name', 'industry', 'total_shares', 'initial_price']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
        
    try:
        company = CompanyService.create_company(
            owner_id=data['owner_id'],
            name=data['name'],
            industry=data['industry'],
            total_shares=data['total_shares'],
            initial_price=data['initial_price']
        )
        
        return jsonify({
            'message': '公司创建成功',
            'company': {
                'id': company.id,
                'name': company.name,
                'industry': company.industry,
                'total_shares': company.total_shares,
                'current_price': float(company.current_price)
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建公司失败'}), 500

@company_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """获取公司信息"""
    try:
        company_info = CompanyService.get_company_info(company_id)
        return jsonify(company_info)
    except Exception as e:
        return jsonify({'error': '获取公司信息失败'}), 500

@company_bp.route('/list', methods=['GET'])
def get_company_list():
    """获取公司列表"""
    try:
        companies = Company.query.all()
        return jsonify({
            'message': '获取成功',
            'data': [company.to_dict() for company in companies]
        })
    except Exception as e:
        current_app.logger.error(f"获取公司列表失败: {str(e)}")
        return jsonify({'message': '获取公司列表失败'}), 500 