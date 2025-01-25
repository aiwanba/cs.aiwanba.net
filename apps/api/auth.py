from flask import Blueprint, request, jsonify
from apps.services.auth_service import AuthService
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    user = AuthService.register(
        data['username'],
        data['email'],
        data['password']
    )
    return jsonify({
        'message': '注册成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    user = AuthService.login(data['username'], data['password'])
    if user:
        login_user(user)
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    return jsonify({'message': '用户名或密码错误'}), 401

@auth_bp.route('/logout')
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'message': '登出成功'}) 