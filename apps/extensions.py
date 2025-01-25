from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# 初始化扩展，但不绑定app
db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' 