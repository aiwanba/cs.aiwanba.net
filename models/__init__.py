from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .company import Company
from .stock import StockHolding, Transaction

# 初始化数据库
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all() 