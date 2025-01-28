from functools import wraps
from flask import request, jsonify, g
import jwt
from config import config

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': '未提供认证token'}), 401
            
        try:
            # 获取token
            token = auth_header.split(' ')[1]
            # 解码token
            payload = jwt.decode(
                token,
                config['default'].SECRET_KEY,
                algorithms=['HS256']
            )
            # 将用户ID存储在g对象中
            g.user_id = payload['user_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function 