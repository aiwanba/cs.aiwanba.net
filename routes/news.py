from flask import Blueprint, request, jsonify, session, render_template
from services.news import NewsService

news_bp = Blueprint('news', __name__)

@news_bp.route('/')
def news_page():
    """新闻主页"""
    active_news = NewsService.get_active_news()
    return render_template('news/index.html', news_list=active_news)

@news_bp.route('/company/<int:company_id>')
def company_news(company_id):
    """公司新闻页面"""
    news_list = NewsService.get_company_news(company_id)
    return render_template('news/company.html', news_list=news_list)

@news_bp.route('/comment', methods=['POST'])
def add_comment():
    """添加评论"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    news_id = data.get('news_id')
    content = data.get('content')
    
    if not all([news_id, content]):
        return jsonify({"success": False, "message": "请填写评论内容"})
        
    success, comment = NewsService.add_comment(news_id, session['user_id'], content)
    if success:
        return jsonify({
            "success": True,
            "message": "评论成功",
            "data": {
                "content": comment.content,
                "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    return jsonify({"success": False, "message": comment}) 