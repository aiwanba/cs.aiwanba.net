from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS
from flask_socketio import SocketIO

# 初始化扩展
db = SQLAlchemy()
cache = Cache()
cors = CORS()
socketio = SocketIO() 