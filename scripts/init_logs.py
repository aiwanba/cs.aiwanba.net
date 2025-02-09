#!/usr/bin/env python3
"""
初始化日志目录和文件
"""
import os
import sys
import logging

def init_logs():
    """初始化日志目录和文件"""
    try:
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(root_dir, 'logs')
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件
        log_files = ['app.log', 'access.log', 'error.log']
        for log_file in log_files:
            log_path = os.path.join(log_dir, log_file)
            if not os.path.exists(log_path):
                open(log_path, 'a').close()
            
            # 设置权限
            os.chmod(log_path, 0o666)
            
        print(f"Log directory initialized: {log_dir}")
        return True
    except Exception as e:
        print(f"Error initializing logs: {e}")
        return False

if __name__ == '__main__':
    success = init_logs()
    sys.exit(0 if success else 1) 