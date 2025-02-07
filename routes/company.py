from flask import Blueprint, request, jsonify
from models.company import Company, db
from routes.notification import send_notification
from datetime import datetime

company_bp = Blueprint('company', __name__)

@company_bp.route('/api/company', methods=['POST'])
def create_company():
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['name', 'industry', 'initial_cash']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 验证初始资金是否足够（至少1000万）
        if data['initial_cash'] < 10000000:
            return jsonify({'error': 'Initial cash must be at least 10 million'}), 400
            
        # 创建公司
        company = Company(
            name=data['name'],
            industry=data['industry'],
            cash=data['initial_cash'],
            stock_price=10.0,  # 固定初始股价
            total_shares=1000000  # 固定总股本
        )
        
        db.session.add(company)
        db.session.commit()
        
        # 创建创始人股东记录
        from models.shareholder import Shareholder
        founder_shares = int(data['initial_cash'] / (company.stock_price * company.total_shares) * company.total_shares)
        shareholder = Shareholder(
            company_id=company.id,
            user_id=request.user_id,  # 假设通过认证中间件设置
            shares=founder_shares
        )
        
        db.session.add(shareholder)
        db.session.commit()
        
        # 发送新公司上市通知
        send_notification(
            'system',
            'info',
            '新公司上市',
            f'新公司{company.name}已成功上市，初始股价{company.stock_price}元',
            company.id
        )
        
        return jsonify({
            'status': 'success',
            'company': company.to_dict(),
            'founder_shares': founder_shares
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_bp.route('/api/company/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict())

@company_bp.route('/api/company/<int:company_id>/shareholders', methods=['GET'])
def get_shareholders(company_id):
    company = Company.query.get_or_404(company_id)
    shareholders = [{
        'user_id': s.user_id,
        'shares': s.shares,
        'percentage': (s.shares / company.total_shares) * 100
    } for s in company.shareholders]
    
    return jsonify(shareholders)

@company_bp.route('/api/company/<int:company_id>/dividend', methods=['POST'])
def distribute_dividend(company_id):
    try:
        data = request.get_json()
        if 'amount_per_share' not in data:
            return jsonify({'error': 'Missing amount_per_share'}), 400
            
        company = Company.query.get_or_404(company_id)
        amount_per_share = float(data['amount_per_share'])
        total_dividend = amount_per_share * company.total_shares
        
        # 检查现金是否足够
        if company.cash < total_dividend:
            return jsonify({'error': 'Insufficient cash for dividend'}), 400
            
        # 扣除公司现金
        company.cash -= total_dividend
        db.session.commit()
        
        # TODO: 给股东分配现金（需要实现用户钱包系统）
        
        return jsonify({
            'status': 'success',
            'total_dividend': total_dividend
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 