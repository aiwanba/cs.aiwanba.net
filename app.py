from flask import Flask, jsonify, request, send_file, Response, redirect
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from openai import OpenAI
from functools import lru_cache
import uuid
from models import db, Conversation, Message
from apscheduler.schedulers.background import BackgroundScheduler
import csv
from io import StringIO, BytesIO
import json
import httpx
from werkzeug.middleware.proxy_fix import ProxyFix
from io import TextIOWrapper

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)  # 添加这行
CORS(app)  # 启用CORS支持

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 配置OpenAI客户端
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
    http_client=httpx.Client(
        timeout=60.0,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    )
)

# 内存缓存，仅用于临时存储响应
response_cache = {}

# 会话过期时间（24小时）
SESSION_EXPIRY = timedelta(hours=24)

def cleanup_expired_sessions():
    """清理过期会话"""
    with app.app_context():
        expiry_time = datetime.utcnow() - SESSION_EXPIRY
        expired_conversations = Conversation.query.filter(
            Conversation.last_active < expiry_time
        ).all()
        
        for conv in expired_conversations:
            db.session.delete(conv)
        
        db.session.commit()

# 设置定时任务，每小时清理一次过期会话
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_sessions, 'interval', hours=1)
scheduler.start()

# 在现有路由前添加URL预处理
@app.before_request
def normalize_request():
    # 自动去除路径末尾的斜杠和空格
    original_path = request.path
    cleaned_path = original_path.rstrip('/ ').lstrip()  # 同时处理左右两侧的空格
    
    # 处理根路径的特殊情况
    if not cleaned_path:
        cleaned_path = '/'
    
    # 只有当清理后的路径有效时才重定向
    if cleaned_path != original_path and len(cleaned_path) > 0:
        return redirect(cleaned_path)

@app.route('/')
def index():
    """保留根路径作为兼容性入口"""
    return redirect('/health')

@app.route('/health')
def health_check():
    """整合健康检查和服务状态"""
    return jsonify({
        "status": "服务正常",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": {
            "database": "数据库连接正常",
            "cache": f"缓存 {len(response_cache)} 条记录",
            "active_sessions": f"当前活动会话数量 {Conversation.query.count()} 条记录"
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        # 如果没有会话ID，创建新的会话
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(id=conversation_id)
            db.session.add(conversation)
        else:
            # 检查会话是否存在且未过期
            conversation = Conversation.query.filter(
                Conversation.id == conversation_id,
                Conversation.last_active >= (datetime.utcnow() - SESSION_EXPIRY)
            ).first()
            
            if not conversation:
                # 自动创建新会话而不是返回错误
                conversation_id = str(uuid.uuid4())
                conversation = Conversation(id=conversation_id)
                db.session.add(conversation)
        
        # 更新最后活动时间
        conversation.last_active = datetime.utcnow()
        
        # 获取历史消息
        messages = [msg.to_dict() for msg in conversation.messages[-9:]]  # 获取最近9条消息
        messages.append({"role": "user", "content": user_message})
        
        # 检查缓存
        cache_key = f"{conversation_id}:{user_message}"
        if cache_key in response_cache:
            return jsonify({
                "status": "success",
                "response": response_cache[cache_key],
                "conversation_id": conversation_id,
                "cached": True
            })
        
        # 调用API获取响应（非流式）
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=4096,
            stream=False  # 明确设置为非流式
        )

        # 获取AI响应（直接获取完整响应）
        response = completion.choices[0].message.content
        
        # 保存用户消息和AI响应到数据库
        user_msg = Message(conversation_id=conversation_id, role='user', content=user_message)
        ai_msg = Message(conversation_id=conversation_id, role='assistant', content=response)
        db.session.add(user_msg)
        db.session.add(ai_msg)
        
        # 更新缓存
        response_cache[cache_key] = response
        
        # 提交数据库事务
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "response": response,
            "conversation_id": conversation_id,
            "cached": False
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    """流式对话接口"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')

        # 会话处理逻辑与普通接口相同
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(id=conversation_id)
            db.session.add(conversation)
        else:
            conversation = Conversation.query.filter(
                Conversation.id == conversation_id,
                Conversation.last_active >= (datetime.utcnow() - SESSION_EXPIRY)
            ).first()
            if not conversation:
                conversation_id = str(uuid.uuid4())
                conversation = Conversation(id=conversation_id)
                db.session.add(conversation)

        conversation.last_active = datetime.utcnow()
        messages = [msg.to_dict() for msg in conversation.messages[-9:]]
        messages.append({"role": "user", "content": user_message})

        def generate():
            with app.app_context():
                # 确保会话对象已存在并提交
                db.session.add(conversation)
                db.session.commit()  # 强制立即提交会话
                
                # 创建用户消息并提交
                user_msg = Message(conversation_id=conversation.id, role='user', content=user_message)
                db.session.add(user_msg)
                db.session.commit()  # 提交用户消息
                
                # 处理API响应...
                completion = client.chat.completions.create(
                    model="deepseek-ai/deepseek-r1",
                    messages=messages,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096,
                    stream=True
                )
                
                full_response = []
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        raw_content = chunk.choices[0].delta.content
                        processed_content = raw_content.replace('**', '')
                        content = json.dumps({'content': processed_content}, ensure_ascii=False)
                        full_response.append(raw_content)  # 收集原始内容用于保存
                        yield f"data: {content}\n\n"
                
                # 最后处理数据库
                try:
                    # 保存AI响应
                    ai_msg = Message(conversation_id=conversation.id, role='assistant', content=''.join(full_response))
                    db.session.add(ai_msg)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"保存消息失败: {str(e)}")

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """获取特定会话的历史记录"""
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({
            "status": "error",
            "message": "Conversation not found"
        }), 404
    
    messages = [msg.to_dict() for msg in conversation.messages]
    return jsonify({
        "status": "success",
        "history": messages,
        "created_at": conversation.created_at.isoformat(),
        "last_active": conversation.last_active.isoformat()
    })

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def clear_conversation(conversation_id):
    """清除特定会话的历史记录"""
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({
            "status": "错误",
            "message": "会话历史未找到"
        }), 404
    
    db.session.delete(conversation)
    db.session.commit()
    
    # 清除相关缓存
    for key in list(response_cache.keys()):
        if key.startswith(f"{conversation_id}:"):
            del response_cache[key]
    
    return jsonify({
        "status": "成功",
        "message": "会话历史已清除"
    })

@app.route('/api/conversations/<conversation_id>/export', methods=['GET'])
def export_conversation(conversation_id):
    """优化后的单会话导出"""
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({
            "status": "error",
            "message": "Conversation not found"
        }), 404
    
    export_format = request.args.get('format', 'json')

    if export_format == 'csv':
        def generate():
            # 创建应用上下文
            with app.app_context():
                # 创建内存写入器
                mem = StringIO()
                writer = csv.writer(mem)
                
                # 写入表头
                writer.writerow(['Timestamp', 'Role', 'Content'])
                yield mem.getvalue()
                mem.seek(0)
                mem.truncate(0)
                
                # 分批查询消息（每次100条）
                query = Message.query.filter_by(
                    conversation_id=conversation_id
                ).yield_per(100)
                
                for msg in query:
                    writer.writerow([
                        msg.timestamp.isoformat(),
                        msg.role,
                        msg.content
                    ])
                    yield mem.getvalue()
                    mem.seek(0)
                    mem.truncate(0)

        headers = {
            'Content-Type': 'text/csv',
            'Content-Disposition': 
                f'attachment; filename=conversation_{conversation_id}.csv'
        }
        return Response(generate(), headers=headers)
    
    elif export_format == 'json':
        # 新增JSON导出处理
        def generate_json():
            with app.app_context():
                data = {
                    'conversation_id': conversation.id,
                    'created_at': conversation.created_at.isoformat(),
                    'last_active': conversation.last_active.isoformat(),
                    'messages': []
                }
                
                # 分批处理消息
                query = Message.query.filter_by(
                    conversation_id=conversation_id
                ).yield_per(100)
                
                for msg in query:
                    data['messages'].append({
                        'timestamp': msg.timestamp.isoformat(),
                        'role': msg.role,
                        'content': msg.content
                    })
                    # 每100条生成部分JSON
                    if len(data['messages']) % 100 == 0:
                        yield json.dumps(data, ensure_ascii=False) + '\n'
                
                # 生成最终结果
                yield json.dumps(data, ensure_ascii=False)
        
        headers = {
            'Content-Type': 'application/json',
            'Content-Disposition': 
                f'attachment; filename=conversation_{conversation_id}.json'
        }
        return Response(generate_json(), headers=headers)
    
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported format, use csv or json"
        }), 400

@app.route('/api/conversations/export-all', methods=['GET'])
def export_all_conversations():
    """批量导出优化版"""
    try:
        export_format = request.args.get('format', 'json')
        
        # 仅处理CSV格式
        if export_format == 'csv':
            def generate_csv():
                # 创建应用上下文
                with app.app_context():
                    # 创建内存写入器
                    mem = StringIO()
                    writer = csv.writer(mem)
                    
                    # 写入表头
                    writer.writerow(['会话ID', '创建时间', '最后活跃时间', '消息数量'])
                    yield mem.getvalue()
                    mem.seek(0)
                    mem.truncate(0)
                    
                    # 分批查询数据库
                    query = Conversation.query.yield_per(100)  # 每次处理100条
                    for conv in query:
                        writer.writerow([
                            conv.id,
                            conv.created_at.isoformat(),
                            conv.last_active.isoformat(),
                            len(conv.messages)
                        ])
                        yield mem.getvalue()
                        mem.seek(0)
                        mem.truncate(0)
            
            # 流式响应
            headers = {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=conversations_export_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
            }
            return Response(generate_csv(), headers=headers)
        
        # 其他格式保持不变...
        
    except Exception as e:
        app.logger.error(f"导出异常: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500
    
# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True) 