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

# 设置进程文件目录（用于停止服务和重启服务，请勿删除）
pidfile = '/www/wwwroot/cs.aiwanba.net/gunicorn.pid'

# 设置访问日志和错误信息日志路径
accesslog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_access.log'
errorlog = '/www/wwwlogs/python/cs_aiwanba_net/gunicorn_error.log'

# 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
# debug:调试级别，记录的信息最多；
# info:普通级别；
# warning:警告消息；
# error:错误消息；
# critical:严重错误消息；
loglevel = 'info' 

# 启动时创建日志目录
import os
os.makedirs('/www/wwwlogs/python/cs_aiwanba_net', exist_ok=True)

# 设置工作目录权限
def when_ready(server):
    """当服务器准备就绪时执行"""
    # 确保日志目录存在并设置权限
    log_dir = '/www/wwwlogs/python/cs_aiwanba_net'
    os.makedirs(log_dir, exist_ok=True)
    os.system(f'chown -R {user}:{user} {log_dir}')
    
    # 确保项目目录权限正确
    project_dir = '/www/wwwroot/cs.aiwanba.net'
    os.system(f'chown -R {user}:{user} {project_dir}')
    
    # 确保 pid 文件权限正确
    if os.path.exists(pidfile):
        os.system(f'chown {user}:{user} {pidfile}')

# 优雅重启时间
graceful_timeout = 30

# 超时时间
timeout = 30

# 进程名称
proc_name = 'cs_aiwanba_net'

# 启动时执行的钩子
def on_starting(server):
    """服务启动时执行"""
    # 初始化日志目录
    os.system('python3 /www/wwwroot/cs.aiwanba.net/scripts/init_logs.py')

# 自定义设置项请写到该处
# 最好以上面相同的格式 <注释 + 换行 + key = value> 进行书写， 
# PS: gunicorn 的配置文件是python扩展形式，即".py"文件，需要注意遵从python语法，
# 如：loglevel的等级是字符串作为配置的，需要用引号包裹起来