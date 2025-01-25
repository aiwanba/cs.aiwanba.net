#!/bin/bash

# 设置工作目录
cd /www/wwwroot/cs.aiwanba.net

# 激活虚拟环境
source venv/bin/activate

# 启动Gunicorn服务
gunicorn -c gunicorn_conf.py app:app 