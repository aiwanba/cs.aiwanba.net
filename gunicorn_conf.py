# 项目目录
chdir = '/www/wwwroot/cs.aiwanba.net'

# 指定进程数
workers = 4

# 指定每个进程开启的线程数
threads = 2

# 启动用户
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