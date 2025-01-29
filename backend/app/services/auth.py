from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app import db

class AuthService:
    @staticmethod
    def register(username, password, email):
        """用户注册"""
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return False, "用户名已存在"
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return False, "邮箱已被注册"
        
        try:
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            return True, user
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def login(username, password):
        """用户登录"""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, "用户不存在"
        
        if not user.check_password(password):
            return False, "密码错误"
        
        if user.status != 1:
            return False, "账号已被禁用"
        
        # 确保user.id转换为字符串
        user_id = str(user.id)
        
        # 生成访问令牌和刷新令牌
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        
        return True, {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def refresh_token(user_id):
        """刷新访问令牌"""
        try:
            # 确保user_id是字符串
            user_id = str(user_id)
            access_token = create_access_token(identity=user_id)
            return True, {"access_token": access_token}
        except Exception as e:
            return False, str(e) 