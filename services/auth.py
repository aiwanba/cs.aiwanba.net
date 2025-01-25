from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

class AuthService:
    """用户认证服务"""
    
    @staticmethod
    def register(username, password, email):
        """用户注册"""
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return False, "用户名已存在"
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return False, "邮箱已被注册"
            
        # 创建新用户，使用werkzeug的密码哈希
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(
            username=username,
            password=hashed_password,  # 存储哈希后的密码
            email=email
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            return True, "注册成功"
        except Exception as e:
            db.session.rollback()
            return False, f"注册失败：{str(e)}"
    
    @staticmethod
    def login(username, password):
        """用户登录"""
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, "用户不存在"
            
        # 添加调试信息
        print("存储的密码哈希:", user.password)
        print("输入的密码:", password)
        print("验证结果:", check_password_hash(user.password, password))
        
        if not check_password_hash(user.password, password):
            return False, "密码错误"
            
        return True, user 