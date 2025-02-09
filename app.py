"""
主应用入口文件
"""
from flask import Flask, request, jsonify, Response, stream_with_context, render_template, send_from_directory
from services.ai_service import AIService
from utils.db_manager import DatabaseManager
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from werkzeug.utils import secure_filename
import hashlib
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5010", "http://127.0.0.1:5010"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'json', 'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化服务
ai_service = AIService()
db_manager = DatabaseManager()

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    """生成唯一的文件名"""
    timestamp = str(int(time.time()))
    name, ext = os.path.splitext(filename)
    hash_str = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:8]
    return f"{name}_{hash_str}{ext}"

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传处理"""
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = get_unique_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            uploaded_files.append({
                'original_name': filename,
                'saved_name': unique_filename,
                'url': f'/uploads/{unique_filename}'
            })
    
    if uploaded_files:
        return jsonify({
            'message': 'Files uploaded successfully',
            'files': uploaded_files
        })
    
    return jsonify({'error': 'No valid files uploaded'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """访问上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        db_manager.execute_query("SELECT 1")
        return jsonify({
            'status': 'ok',
            'database': 'connected'
        })
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        app.logger.info("Received chat request")
        data = request.get_json()
        app.logger.info(f"Request data: {data}")
        
        prompt = data.get('prompt')
        stream = data.get('stream', True)
        
        if not prompt:
            app.logger.warning("Empty prompt received")
            return jsonify({'error': 'Prompt is required'}), 400
            
        app.logger.info(f"Processing prompt: {prompt[:100]}...")
        
        # 处理特殊命令
        if prompt.startswith('translate:'):
            # 处理翻译命令
            _, text = prompt.split(':', 1)
            prompt = f"请将以下文本翻译: {text.strip()}"
        elif prompt.startswith('py:'):
            # 处理Python代码
            _, code = prompt.split(':', 1)
            prompt = f"请解释并执行以下Python代码:\n```python\n{code.strip()}\n```"
        elif prompt.startswith('js:'):
            # 处理JavaScript代码
            _, code = prompt.split(':', 1)
            prompt = f"请解释并执行以下JavaScript代码:\n```javascript\n{code.strip()}\n```"
            
        if stream:
            app.logger.info("Using streaming response")
            def generate():
                try:
                    for chunk in ai_service.generate_response(prompt, stream=True):
                        app.logger.debug(f"Streaming chunk: {chunk[:50]}...")
                        yield chunk
                except Exception as e:
                    app.logger.error(f"Error in stream generation: {str(e)}")
                    yield f"Error: {str(e)}"
            
            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream'
            )
        else:
            app.logger.info("Using non-streaming response")
            response = ai_service.generate_response(prompt, stream=False)
            return jsonify({'response': response})
            
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 