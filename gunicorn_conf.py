import multiprocessing
import os

# 设置工作目录
chdir = '/www/wwwroot/cs.aiwanba.net'

# 绑定的ip与端口
bind = "127.0.0.1:5010"

# 进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'eventlet'  # 使用eventlet作为异步工作模式，支持WebSocket

# 线程数
threads = 2

# 超时时间
timeout = 30

# 日志配置
accesslog = "/www/wwwlogs/python/cs_aiwanba_net/gunicorn_access.log"
errorlog = "/www/wwwlogs/python/cs_aiwanba_net/gunicorn_error.log"
loglevel = 'info'

# 进程名称
proc_name = 'cs_aiwanba_net'

# 工作模式
worker_connections = 2000  # eventlet模式下的最大并发连接数

# 安全配置
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 启动用户
user = 'www'

# 设置进程文件目录
pidfile = '/www/wwwroot/cs.aiwanba.net/gunicorn.pid'

# 启动模式
worker_class = 'uvicorn.workers.UvicornWorker'

# 设置访问日志和错误信息日志路径
accesslog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_acess.log'
errorlog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_error.log'

# 日志级别
loglevel = 'info' 