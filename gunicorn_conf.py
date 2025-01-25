import multiprocessing

# 监听地址和端口
bind = "0.0.0.0:5010"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'uvicorn.workers.UvicornWorker'

# 每个工作进程的线程数
threads = 2

# 用户
user = 'www'

# 日志级别
loglevel = 'info'

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 访问日志文件
accesslog = "/www/wwwlogs/cs.aiwanba.net.access.log"

# 错误日志文件
errorlog = "/www/wwwlogs/cs.aiwanba.net.error.log" 