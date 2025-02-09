from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用CORS支持

@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "Server is running",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    # 开发环境下使用
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True) 