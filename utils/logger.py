import os
import logging
from logging.handlers import RotatingFileHandler
from config.settings import Config

def setup_logger(app):
    """配置日志系统"""
    
    # 创建日志目录
    log_dir = os.path.dirname(Config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志格式
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(Config.LOG_LEVEL)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(Config.LOG_LEVEL)
    
    # 配置Flask应用日志
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(Config.LOG_LEVEL)
    
    # 配置SQLAlchemy日志
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return app.logger 