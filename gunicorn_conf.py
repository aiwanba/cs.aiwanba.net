# Gunicorn配置
bind = '0.0.0.0:5010'
workers = 4
threads = 2
worker_class = 'sync'
pidfile = 'gunicorn.pid'
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info' 