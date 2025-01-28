from flask import Blueprint, request
from app.services.auth import AuthService
from app.utils.response import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not all([username, password, email]):
        return error_response("请填写完整信息")
    
    success, result = AuthService.register(username, password, email)
    if success:
        return success_response(result.to_dict(), "注册成功")
    return error_response(result)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return error_response("请填写用户名和密码")
    
    success, result = AuthService.login(username, password)
    if success:
        return success_response(result, "登录成功")
    return error_response(result)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    user_id = get_jwt_identity()
    success, result = AuthService.refresh_token(user_id)
    if success:
        return success_response(result, "令牌刷新成功")
    return error_response(result) 