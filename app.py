"""
主应用入口文件
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from services.ai_service import AIService
from utils.db_manager import DatabaseManager
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from config.ai_config import DEEPSEEK_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 启用CORS

# 初始化服务
ai_service = AIService()
db_manager = DatabaseManager()

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
    """
    聊天接口
    支持流式和非流式响应
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        stream = data.get('stream', True)  # 默认使用流式响应
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
            
        if stream:
            def generate():
                for chunk in ai_service.generate_response(prompt, stream=True):
                    yield chunk
            
            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream'
            )
        else:
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
    # 开发环境配置
    app.run(host='0.0.0.0', port=5010, debug=True) 