from flask import Blueprint, request, jsonify, session
from services.auth import AuthService

auth_bp = Blueprint('auth', __name__)

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