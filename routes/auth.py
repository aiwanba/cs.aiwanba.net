from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from services.auth import AuthService
from models.user import User

auth_bp = Blueprint('auth', __name__)

# 添加登录页面路由
@auth_bp.route('/login')
def login_page():
    """登录页面"""
    return render_template('auth/login.html')

# 添加注册页面路由
@auth_bp.route('/register')
def register_page():
    """注册页面"""
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return jsonify({"success": False, "message": "请填写完整信息"})
    
    success, message = AuthService.register(username, password, email)
    return jsonify({"success": success, "message": message})

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({"success": False, "message": "请填写用户名和密码"})
    
    success, result = AuthService.login(username, password)
    if success:
        session['user_id'] = result.id
        return jsonify({
            "success": True,
            "message": "登录成功",
            "data": {
                "username": result.username,
                "email": result.email,
                "balance": float(result.balance)
            }
        })
    return jsonify({"success": False, "message": result})

@auth_bp.route('/logout')
def logout():
    """退出登录"""
    session.pop('user_id', None)
    return redirect(url_for('index'))

@auth_bp.route('/user_info')
def get_user_info():
    """获取用户信息"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401
        
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"success": False, "message": "用户不存在"}), 404
        
    return jsonify({
        "success": True,
        "data": {
            "username": user.username,
            "email": user.email,
            "balance": float(user.balance)
        }
    }) 