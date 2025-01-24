# Gunicorn生产环境配置
import multiprocessing

# 项目目录
chdir = '/www/wwwroot/cs.aiwanba.net'

# 工作进程数 (推荐设置：CPU核心数*2+1)
workers = multiprocessing.cpu_count() * 2 + 1

# 每个工作进程的线程数
threads = 2

# 启动用户
user = 'www'

# 绑定地址和端口
bind = '0.0.0.0:5010'

# 进程文件（用于服务管理）
pidfile = '/www/wwwroot/cs.aiwanba.net/gunicorn.pid'

# 访问日志配置
accesslog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_access.log'
errorlog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_error.log'

# 日志级别
loglevel = 'info'

# 工作模式
worker_class = 'gevent'

# 最大并发连接数
worker_connections = 1000

# 超时设置
timeout = 30
keepalive = 2

# 服务器钩子（可选）
def post_fork(server, worker):
    server.log.info("Worker %s (pid: %s) spawned", worker.name, worker.pid) 