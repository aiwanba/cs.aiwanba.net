import os
from datetime import timedelta

class Config:
    """项目配置类"""
    
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://root:password@localhost/stock_game')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/app.log'
    
    # 性能配置
    TEMPLATES_AUTO_RELOAD = DEBUG
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 业务配置
    MARKET_UPDATE_INTERVAL = 60  # 市场数据更新间隔(秒)
    AI_TRADE_INTERVAL = 300  # AI交易间隔(秒)
    NEWS_UPDATE_INTERVAL = 600  # 新闻更新间隔(秒)
    MAX_COMPANIES_PER_USER = 3  # 每个用户最多创建的公司数
    MIN_STOCK_PRICE = 1  # 最低股票价格
    MAX_STOCK_PRICE = 1000000  # 最高股票价格
    TRADE_FEE_RATE = 0.001  # 交易手续费率 