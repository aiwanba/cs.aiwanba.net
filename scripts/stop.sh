#!/bin/bash

# 获取进程ID
pid=$(cat /www/wwwroot/cs.aiwanba.net/gunicorn.pid)

# 停止服务
kill -TERM $pid 