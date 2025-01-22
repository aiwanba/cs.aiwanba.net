from flask import Flask
from config import Config

# 创建 Flask 应用实例
app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库（稍后添加）
# from .models import db
# db.init_app(app)

# 注册路由（稍后添加）
from . import routes