from apps.models.user import User
from app import db

class AuthService:
    @staticmethod
    def register(username, email, password):
        """用户注册"""
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def login(username, password):
        """用户登录"""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None 