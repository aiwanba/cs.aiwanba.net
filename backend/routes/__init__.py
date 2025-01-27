from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
company_bp = Blueprint('company', __name__)
stock_bp = Blueprint('stock', __name__)
bank_bp = Blueprint('bank', __name__)

# 导入路由处理函数
from . import auth, company, stock, bank 