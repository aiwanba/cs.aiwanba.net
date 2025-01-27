class Config:
    # 基础配置
    DEBUG = False
    SECRET_KEY = 'your-secret-key'  # 请更改为随机字符串
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:5010']

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 