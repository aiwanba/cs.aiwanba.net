from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from apps.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/create', methods=['POST'])
@login_required
def create_ai():
    """创建AI玩家"""
    data = request.get_json()
    ai = AIService.create_ai_player(
        data['name'],
        float(data.get('balance', 10000.0)),
        float(data.get('risk_preference', 0.5))
    )
    
    return jsonify({
        'message': 'AI玩家创建成功',
        'ai': {
            'id': ai.id,
            'name': ai.name,
            'balance': float(ai.balance),
            'risk_preference': ai.risk_preference
        }
    })

@ai_bp.route('/decisions')
@login_required
def get_decisions():
    """获取AI决策"""
    results = AIService.make_decisions()
    return jsonify({'decisions': results})

@ai_bp.route('/run', methods=['POST'])
@login_required
def run_trading():
    """手动触发AI交易（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({'message': '权限不足'}), 403
        
    results = AIService.run_ai_trading()
    return jsonify({
        'message': 'AI交易执行完成',
        'results': results
    })

@ai_bp.route('/market/analysis', methods=['GET'])
@login_required
def get_market_analysis():
    """获取市场分析数据"""
    market_data = AIService.analyze_market()
    return jsonify({'market_data': market_data}) 