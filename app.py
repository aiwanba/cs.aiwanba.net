# 导入 Flask 应用实例
from backend.app import app

# 如果是直接运行这个文件，启动 Flask 应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 