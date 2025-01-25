from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from services.social import SocialService

social_bp = Blueprint('social', __name__)

@social_bp.route('/')
def social_page():
    """社交主页"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('social/index.html')

@social_bp.route('/teams')
def teams_page():
    """团队列表页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('social/teams.html')

@social_bp.route('/team/create', methods=['GET', 'POST'])
def create_team():
    """创建团队"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
        
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not all([name, description]):
            return jsonify({"success": False, "message": "请填写完整信息"})
            
        success, result = SocialService.create_team(name, description, session['user_id'])
        if success:
            return jsonify({
                "success": True,
                "message": "创建成功",
                "data": {"team_id": result.id}
            })
        return jsonify({"success": False, "message": result})
        
    return render_template('social/create_team.html')

@social_bp.route('/team/<int:team_id>')
def team_page(team_id):
    """团队详情页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('social/team.html', team_id=team_id)

@social_bp.route('/team/join', methods=['POST'])
def join_team():
    """加入团队"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    team_id = data.get('team_id')
    
    if not team_id:
        return jsonify({"success": False, "message": "参数错误"})
        
    success, result = SocialService.join_team(team_id, session['user_id'])
    if success:
        return jsonify({"success": True, "message": "加入成功"})
    return jsonify({"success": False, "message": result})

@social_bp.route('/discussion/create', methods=['POST'])
def create_discussion():
    """创建讨论"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    team_id = data.get('team_id')
    title = data.get('title')
    content = data.get('content')
    
    if not all([team_id, title, content]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = SocialService.create_discussion(
        team_id, session['user_id'], title, content)
    if success:
        return jsonify({
            "success": True,
            "message": "发布成功",
            "data": {"discussion_id": result.id}
        })
    return jsonify({"success": False, "message": result})

@social_bp.route('/discussion/comment', methods=['POST'])
def add_comment():
    """添加评论"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    discussion_id = data.get('discussion_id')
    content = data.get('content')
    
    if not all([discussion_id, content]):
        return jsonify({"success": False, "message": "请填写评论内容"})
        
    success, result = SocialService.add_comment(
        discussion_id, session['user_id'], content)
    if success:
        return jsonify({"success": True, "message": "评论成功"})
    return jsonify({"success": False, "message": result})

@social_bp.route('/message/send', methods=['POST'])
def send_message():
    """发送私信"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})
        
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not all([receiver_id, content]):
        return jsonify({"success": False, "message": "请填写完整信息"})
        
    success, result = SocialService.send_message(
        session['user_id'], receiver_id, content)
    if success:
        return jsonify({"success": True, "message": "发送成功"})
    return jsonify({"success": False, "message": result})

@social_bp.route('/messages')
def messages_page():
    """消息页面"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('social/messages.html') 