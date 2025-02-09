# 项目目录
chdir = '/www/wwwroot/cs.aiwanba.net'

# 指定进程数
workers = 4

# 指定每个进程开启的线程数
threads = 2

#启动用户
user = 'www'

# 启动模式
worker_class = 'sync'

# 绑定的ip与端口
bind = '0.0.0.0:5010' 

# 设置进程文件目录
pidfile = '/www/wwwroot/cs.aiwanba.net/gunicorn.pid'

# 设置访问日志和错误信息日志路径
accesslog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_acess.log'
errorlog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_error.log'

# 日志级别
loglevel = 'info'

# 设置守护进程
daemon = True

# 设置超时时间
timeout = 30

# 设置最大并发量
max_requests = 2000

# 每个worker最大并发量
worker_connections = 1000

# 优雅重启时间
graceful_timeout = 30

# 重启时间
reload_engine = 'auto'

# 重启间隔
reload_extra_files = [] 