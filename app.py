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
import uuid
from logging.handlers import RotatingFileHandler

# 创建 Flask 应用
app = Flask(__name__)

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置应用日志
app_log_file = os.path.join(log_dir, 'app.log')
file_handler = RotatingFileHandler(
    app_log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 配置 Flask 应用日志
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# 配置 Werkzeug 访问日志
werkzeug_logger = logging.getLogger('werkzeug')
access_log_file = os.path.join(log_dir, 'access.log')
access_handler = RotatingFileHandler(
    access_log_file,
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8'
)
access_handler.setFormatter(formatter)
werkzeug_logger.addHandler(access_handler)
werkzeug_logger.setLevel(logging.INFO)

# 加载环境变量
load_dotenv()

# 配置 CORS
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
        session_id = data.get('session_id')
        stream = data.get('stream', True)
        
        if not prompt:
            app.logger.warning("Empty prompt received")
            return jsonify({'error': 'Prompt is required'}), 400
            
        # 如果没有会话ID，创建新会话
        if not session_id:
            session_id = str(uuid.uuid4())
            title = prompt[:30] + "..."  # 使用首条消息作为标题
            success = db_manager.create_session(session_id, title)
            if not success:
                app.logger.error("Failed to create session")
                return jsonify({'error': 'Failed to create session'}), 500
        
        # 保存用户消息
        if not db_manager.save_message(session_id, 'user', prompt):
            app.logger.error("Failed to save user message")
            return jsonify({'error': 'Failed to save message'}), 500
            
        app.logger.info(f"Processing prompt: {prompt[:100]}...")
        
        # 获取历史消息
        history = db_manager.get_session_messages(session_id)
            
        if stream:
            app.logger.info("Using streaming response")
            def generate():
                full_response = ''
                try:
                    for chunk in ai_service.generate_response(prompt, history=history, stream=True):
                        app.logger.debug(f"Streaming chunk: {chunk[:50]}...")
                        full_response += chunk
                        yield chunk
                    
                    # 在流式响应完成后保存AI响应
                    app.logger.info("Stream completed, saving AI response")
                    if not db_manager.save_message(session_id, 'assistant', full_response):
                        app.logger.error("Failed to save AI response after streaming")
                except Exception as e:
                    app.logger.error(f"Error in stream generation: {str(e)}")
                    yield f"Error: {str(e)}"
            
            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream'
            )
        else:
            app.logger.info("Using non-streaming response")
            response = ai_service.generate_response(prompt, history=history, stream=False)
            # 保存AI响应
            if not db_manager.save_message(session_id, 'assistant', response):
                app.logger.error("Failed to save AI response")
            return jsonify({'response': response, 'session_id': session_id})
            
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """获取所有会话"""
    try:
        sessions = db_manager.get_all_sessions()
        return jsonify(sessions)
    except Exception as e:
        app.logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    try:
        success = db_manager.delete_session(session_id)
        if success:
            return jsonify({'message': 'Session deleted'})
        return jsonify({'error': 'Failed to delete session'}), 500
    except Exception as e:
        app.logger.error(f"Error deleting session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sessions/<session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """获取会话的所有消息"""
    try:
        app.logger.info(f"Getting messages for session: {session_id}")
        messages = db_manager.get_session_messages(session_id)
        app.logger.info(f"Retrieved {len(messages)} messages")
        return jsonify(messages)
    except Exception as e:
        app.logger.error(f"Error getting session messages: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """调试数据库内容"""
    try:
        db_manager.debug_database()
        return jsonify({'message': 'Check server logs for database content'})
    except Exception as e:
        app.logger.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/debug/messages/<session_id>', methods=['GET'])
def debug_messages(session_id):
    """调试会话消息"""
    try:
        connection = db_manager.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 直接查询数据库
        cursor.execute("""
            SELECT * FROM chat_history 
            WHERE session_id = %s 
            ORDER BY id ASC
        """, (session_id,))
        
        messages = cursor.fetchall()
        return jsonify({
            'count': len(messages),
            'messages': messages
        })
    except Exception as e:
        app.logger.error(f"Error in debug messages: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

def init_app():
    """应用初始化"""
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 初始化数据库表
    try:
        with open('sql/chat_history.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')
        
        for command in sql_commands:
            if command.strip():
                try:
                    db_manager.execute_query(command)
                except Exception as e:
                    app.logger.error(f"Error creating table: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error reading SQL file: {str(e)}")

# 在应用启动前调用初始化
init_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 