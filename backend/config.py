import os

class Config:
    # 基础配置
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost/cs_aiwanba_net'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # CORS配置 - 需要修改允许的源
    CORS_ORIGINS = ['http://localhost:3000']  # 修改这里，允许前端开发服务器的域名

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 