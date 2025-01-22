from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 创建Flask应用
app = Flask(__name__)

# 初始化数据库
db = SQLAlchemy(app) 