from flask import Blueprint, jsonify
from models.company import Company

market_bp = Blueprint('market', __name__)

@market_bp.route('/api/market', methods=['GET'])
def get_market_data():
    """获取市场数据"""
    companies = Company.query.all()
    return jsonify({
        'companies': [company.to_dict() for company in companies]
    }) 