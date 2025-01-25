class Config:
    """项目配置类"""
    # 基本配置
    DEBUG = False
    SECRET_KEY = 'your-secret-key'  # 请更改为随机字符串
    
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'cs_aiwanba_net'
    MYSQL_PASSWORD = 'sQz9HSnF5ZcXj9SX'
    MYSQL_DB = 'cs_aiwanba_net'
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 