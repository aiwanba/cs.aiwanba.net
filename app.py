from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
import urllib3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import sqlite3

# 禁用不安全的 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# 存储对话历史
conversations = []

# 存储当前会话的消息历史
current_conversation = {
    'id': None,
    'messages': []
}

load_dotenv()

API_KEY = os.getenv('NVIDIA_API_KEY')
BASE_URL = os.getenv('NVIDIA_API_BASE_URL', 'https://integrate.api.nvidia.com/v1')

def create_client():
    return OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        timeout=30,  # 添加超时
        max_retries=3  # 添加重试
    )

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations
        (id INTEGER PRIMARY KEY, timestamp TEXT, messages TEXT)
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        stream = data.get('stream', False)
        conversation_id = data.get('conversation_id')
        
        # 获取或创建会话
        global current_conversation
        if conversation_id is not None:
            # 使用现有会话
            current_conversation = next(
                (conv for conv in conversations if conv['id'] == conversation_id),
                {'id': conversation_id, 'messages': []}
            )
        elif current_conversation['id'] is None:
            # 创建新会话
            conversation_id = len(conversations)
            current_conversation = {
                'id': conversation_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'messages': []
            }
        
        # 添加用户消息
        current_conversation['messages'].append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # 构建完整的对话历史
        messages = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in current_conversation['messages']
        ]
        
        # 添加请求超时处理
        client = create_client()
        
        if stream:
            def generate():
                try:
                    completion = client.chat.completions.create(
                        model="deepseek-ai/deepseek-r1",
                        messages=messages,
                        temperature=0.6,
                        top_p=0.7,
                        max_tokens=4096,
                        stream=True,
                        timeout=30  # 添加超时设置
                    )
                    
                    full_response = ""
                    for chunk in completion:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            # 添加心跳包，防止连接断开
                            yield f"data: {json.dumps({'content': full_response, 'heartbeat': True})}\n\n"
                    
                    # 保存AI响应到对话历史
                    current_conversation['messages'].append({
                        'role': 'assistant',
                        'content': full_response,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    if current_conversation not in conversations:
                        conversations.append(current_conversation)
                    
                    yield f"data: {json.dumps({'content': full_response, 'done': True, 'conversation_id': current_conversation['id']})}\n\n"
                    
                except Exception as e:
                    # 添加更详细的错误信息
                    error_msg = f"错误: {str(e)}"
                    print(f"Stream Error: {error_msg}")  # 添加日志
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                
            return Response(generate(), mimetype='text/event-stream')
        else:
            completion = client.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=messages,  # 使用完整的对话历史
                temperature=0.6,
                top_p=0.7,
                max_tokens=4096,
                stream=False
            )
            
            response = completion.choices[0].message.content
            
            # 保存AI响应到对话历史
            current_conversation['messages'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # 如果是新会话，添加到会话列表
            if current_conversation not in conversations:
                conversations.append(current_conversation)
            
            return jsonify({
                "success": True,
                "response": response,
                "conversation_id": current_conversation['id']
            })
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history')
def get_history():
    return jsonify(conversations)

@app.route('/api/conversation/<int:conversation_id>')
def get_conversation(conversation_id):
    conversation = next(
        (conv for conv in conversations if conv['id'] == conversation_id),
        None
    )
    if conversation:
        return jsonify(conversation)
    return jsonify({"error": "Conversation not found"}), 404

@app.route('/api/new-conversation', methods=['POST'])
def new_conversation():
    global current_conversation
    current_conversation = {
        'id': len(conversations),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'messages': []
    }
    return jsonify({"success": True, "conversation_id": current_conversation['id']})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({
        'api_key': API_KEY,
        'api_base_url': BASE_URL
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_base_url = data.get('api_base_url')
        
        # 更新环境变量
        os.environ['NVIDIA_API_KEY'] = api_key
        os.environ['NVIDIA_API_BASE_URL'] = api_base_url
        
        # 更新 .env 文件
        with open('.env', 'w') as f:
            f.write(f'NVIDIA_API_KEY={api_key}\n')
            f.write(f'NVIDIA_API_BASE_URL={api_base_url}\n')
        
        # 重新加载环境变量
        load_dotenv(override=True)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5010, debug=True) 