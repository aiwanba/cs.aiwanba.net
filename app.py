# [功能] 用户模块初始化 - 李四 2024-03-20
from flask import Flask
from models.user import User  # 来自提交a1b2c3d

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome" 