import os

class Config:
    """配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:password@localhost:3306/stock_game'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 游戏相关配置
    INITIAL_BALANCE = 100000  # 玩家初始资金
    MIN_STOCK_PRICE = 1  # 最低股票价格
    MAX_STOCK_PRICE = 1000  # 最高股票价格 