from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from apps.services.news_service import NewsService
from apps.models.company import Company

news_bp = Blueprint('news', __name__)

@news_bp.route('/list', methods=['GET'])
def get_news_list():
    """获取新闻列表"""
    news_type = request.args.get('type')
    company_id = request.args.get('company_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    news_list = NewsService.get_news_list(news_type, company_id, limit)
    
    return jsonify({
        'news': [{
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'type': news.type,
            'company_name': news.company.name if news.company else None,
            'impact': news.impact,
            'created_at': news.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for news in news_list]
    })

@news_bp.route('/create', methods=['POST'])
@login_required
def create_news():
    """创建新闻"""
    data = request.get_json()
    news = NewsService.create_news(
        data['title'],
        data['content'],
        data['type'],
        data.get('company_id'),
        data.get('impact', 0)
    )
    
    return jsonify({
        'message': '新闻创建成功',
        'news': {
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'type': news.type,
            'created_at': news.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@news_bp.route('/generate/market', methods=['POST'])
@login_required
def generate_market_news():
    """生成市场新闻（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({'message': '权限不足'}), 403
        
    news = NewsService.generate_market_news()
    return jsonify({
        'message': '市场新闻生成成功',
        'news': {
            'id': news.id,
            'title': news.title,
            'impact': news.impact
        }
    })

@news_bp.route('/generate/company/<int:company_id>', methods=['POST'])
@login_required
def generate_company_news(company_id):
    """生成公司新闻（仅管理员）"""
    if not current_user.is_admin:
        return jsonify({'message': '权限不足'}), 403
        
    company = Company.query.get_or_404(company_id)
    news = NewsService.generate_company_news(company)
    return jsonify({
        'message': '公司新闻生成成功',
        'news': {
            'id': news.id,
            'title': news.title,
            'impact': news.impact
        }
    }) 