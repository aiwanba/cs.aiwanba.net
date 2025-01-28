from flask import jsonify, request, current_app
from . import company_bp
from services.company import CompanyService
from app import db
from models import Company

@company_bp.route('/create', methods=['POST'])
def create_company():
    """创建公司"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['owner_id', 'name', 'industry', 'total_shares', 'initial_price']
        if not all(k in data for k in required_fields):
            return jsonify({'error': '缺少必要字段'}), 400
            
        # 添加详细的日志
        current_app.logger.info(f"Creating company with data: {data}")
        
        # 验证数值范围
        if not (100000 <= data['total_shares'] <= 1000000):
            return jsonify({'error': '总股本必须在10万到100万股之间'}), 400
            
        if not (10 <= float(data['initial_price']) <= 100):
            return jsonify({'error': '初始股价必须在10-100元之间'}), 400
        
        company = CompanyService.create_company(
            owner_id=data['owner_id'],
            name=data['name'],
            industry=data['industry'],
            total_shares=data['total_shares'],
            initial_price=data['initial_price']
        )
        
        return jsonify({
            'message': '公司创建成功',
            'company': company.to_dict()
        }), 201
        
    except ValueError as e:
        current_app.logger.error(f"Value Error in company creation: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating company: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '创建公司失败'}), 500

@company_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """获取公司信息"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # 获取股东信息
        shareholders = []
        try:
            for stock in company.stocks:
                if stock.shares > 0:  # 只显示持有股份的股东
                    percentage = (stock.shares / company.total_shares) * 100
                    shareholders.append({
                        'username': stock.owner.username,
                        'shares': stock.shares,
                        'percentage': percentage
                    })
        except Exception as e:
            current_app.logger.error(f"获取股东信息失败: {str(e)}")
            shareholders = []  # 如果获取股东信息失败，返回空列表
        
        # 构建返回数据
        company_data = company.to_dict()
        company_data['shareholders'] = shareholders
        
        return jsonify({
            'message': '获取成功',
            'data': company_data
        })
    except Exception as e:
        current_app.logger.error(f"获取公司信息失败: {str(e)}")
        db.session.rollback()  # 回滚事务
        return jsonify({'message': '获取公司信息失败'}), 500

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