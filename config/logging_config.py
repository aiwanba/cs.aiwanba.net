import os
import logging
from logging.handlers import RotatingFileHandler
from utils.log_filters import HealthCheckFilter, StaticFileFilter, DuplicateFilter

def setup_logging(app, log_dir):
    """配置日志系统"""
    os.makedirs(log_dir, exist_ok=True)
    
    # 应用日志配置
    app_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 访问日志配置（简化格式）
    access_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 移除现有的处理器
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # 应用日志处理器
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setFormatter(app_formatter)
    app_handler.setLevel(logging.INFO)
    
    # 访问日志处理器
    access_handler = RotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    access_handler.setFormatter(access_formatter)
    access_handler.setLevel(logging.INFO)
    
    # 错误日志处理器
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(app_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 配置根日志记录器
    logging.basicConfig(level=logging.INFO)
    root_logger = logging.getLogger()
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # 配置 Flask 应用日志
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)
    
    # 配置 Werkzeug 访问日志
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.addHandler(access_handler)
    
    # 添加过滤器
    health_filter = HealthCheckFilter()
    static_filter = StaticFileFilter()
    duplicate_filter = DuplicateFilter()
    
    app_handler.addFilter(health_filter)
    app_handler.addFilter(static_filter)
    app_handler.addFilter(duplicate_filter)
    
    access_handler.addFilter(health_filter)
    access_handler.addFilter(static_filter)
    access_handler.addFilter(duplicate_filter)
    
    return {
        'app_handler': app_handler,
        'access_handler': access_handler,
        'error_handler': error_handler
    } 