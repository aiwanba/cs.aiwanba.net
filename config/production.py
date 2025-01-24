import os

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置（用于缓存和WebSocket）
    REDIS_URL = 'redis://localhost:6379/0'
    
    # 日志配置
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # WebSocket配置
    SOCKET_IO_PING_TIMEOUT = 10
    SOCKET_IO_PING_INTERVAL = 25 