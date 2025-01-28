from flask import jsonify, request, current_app
from werkzeug.security import generate_password_hash
from decimal import Decimal
from . import auth_bp
from models import User
from extensions import db

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'message': '缺少必要字段'}), 400
            
        username = data['username']
        email = data['email']
        password = data['password']
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({'message': '用户名长度必须在3-20个字符之间'}), 400
            
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'message': '密码长度不能小于6个字符'}), 400
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '用户名已存在'}), 400
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'message': '邮箱已被注册'}), 400
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        user.balance = Decimal('1000000')  # 初始资金 100 万
        
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"数据库错误: {str(e)}")
            return jsonify({'message': '数据库错误'}), 500
        
        return jsonify({
            'message': '注册成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"注册失败: {str(e)}")
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': '缺少必要字段'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成 JWT token
    token = user.generate_token()  # 需要在 User 模型中实现此方法
    
    return jsonify({
        'message': '登录成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'token': token
    }) 