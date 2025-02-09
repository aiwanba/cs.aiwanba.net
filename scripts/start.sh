#!/bin/bash

# 项目根目录
PROJECT_DIR="/www/wwwroot/cs.aiwanba.net"
LOG_DIR="/www/wwwlogs/python/cs_aiwanba_net"

# 确保目录存在
mkdir -p "$LOG_DIR"

# 激活虚拟环境
source "$PROJECT_DIR/.venv/bin/activate"

# 初始化日志
python "$PROJECT_DIR/scripts/init_logs.py"

# 使用 gunicorn 启动应用
exec gunicorn wsgi:application \
    -c "$PROJECT_DIR/gunicorn_conf.py" \
    --daemon 