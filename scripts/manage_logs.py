#!/usr/bin/env python3
"""
日志管理脚本
用于创建日志目录、设置权限、清理旧日志等
"""
import os
import sys
import shutil
import logging
from datetime import datetime, timedelta

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

# 日志文件
LOG_FILES = {
    'app': 'app.log',
    'access': 'access.log',
    'error': 'error.log'
}

def setup_logging():
    """配置脚本日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def create_log_dir():
    """创建日志目录并设置权限"""
    try:
        # 创建目录
        os.makedirs(LOG_DIR, exist_ok=True)
        os.chmod(LOG_DIR, 0o755)
        logging.info(f"Created log directory: {LOG_DIR}")
        
        # 创建日志文件
        for log_name, log_file in LOG_FILES.items():
            log_path = os.path.join(LOG_DIR, log_file)
            if not os.path.exists(log_path):
                open(log_path, 'a').close()
            os.chmod(log_path, 0o666)
            logging.info(f"Created log file: {log_path}")
            
        return True
    except Exception as e:
        logging.error(f"Error creating log directory: {e}")
        return False

def rotate_logs(max_size_mb=10, keep_days=7):
    """轮转日志文件"""
    try:
        now = datetime.now()
        max_size = max_size_mb * 1024 * 1024  # 转换为字节
        
        for log_name, log_file in LOG_FILES.items():
            log_path = os.path.join(LOG_DIR, log_file)
            if not os.path.exists(log_path):
                continue
                
            # 检查文件大小
            if os.path.getsize(log_path) > max_size:
                timestamp = now.strftime('%Y%m%d_%H%M%S')
                backup_path = f"{log_path}.{timestamp}"
                shutil.copy2(log_path, backup_path)
                open(log_path, 'w').close()  # 清空原文件
                logging.info(f"Rotated log file: {log_path} -> {backup_path}")
                
        # 清理旧日志
        cleanup_old_logs(keep_days)
        return True
    except Exception as e:
        logging.error(f"Error rotating logs: {e}")
        return False

def cleanup_old_logs(keep_days):
    """清理指定天数之前的日志"""
    try:
        now = datetime.now()
        cutoff = now - timedelta(days=keep_days)
        
        for filename in os.listdir(LOG_DIR):
            if not any(filename.startswith(log_file) for log_file in LOG_FILES.values()):
                continue
                
            filepath = os.path.join(LOG_DIR, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mtime < cutoff:
                os.remove(filepath)
                logging.info(f"Removed old log file: {filepath}")
        return True
    except Exception as e:
        logging.error(f"Error cleaning up old logs: {e}")
        return False

def main():
    """主函数"""
    setup_logging()
    
    if len(sys.argv) < 2:
        print("Usage: manage_logs.py [create|rotate|cleanup]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == 'create':
        success = create_log_dir()
    elif action == 'rotate':
        max_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        success = rotate_logs(max_size_mb=max_size)
    elif action == 'cleanup':
        keep_days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        success = cleanup_old_logs(keep_days)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
        
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 