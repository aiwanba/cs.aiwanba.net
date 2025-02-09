"""
WSGI入口文件
"""
from app import app

# 提供给 gunicorn 的 application 对象
application = app 