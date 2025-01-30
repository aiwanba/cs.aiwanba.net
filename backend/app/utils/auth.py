from functools import wraps
from flask import request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response import error_response
from app.models.user import User

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.status != 1:
                return error_response("用户不存在或已被禁用", 401)
            g.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return error_response("未登录或登录已过期", 401)
    return decorated

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.status != 1 or not user.is_admin:
                return error_response("需要管理员权限", 403)
            g.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return error_response("未登录或登录已过期", 401)
    return decorated 