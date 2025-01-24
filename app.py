from flask import Flask
import pymysql

app = Flask(__name__)

# 生产环境日志配置
if __name__ != '__main__':
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# 数据库连接配置
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='cs_aiwanba_net',
        password='sQz9HSnF5ZcXj9SX',
        database='cs_aiwanba_net',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return 'Stock Trading Game'

if __name__ == '__main__':
    app.run(debug=True) 