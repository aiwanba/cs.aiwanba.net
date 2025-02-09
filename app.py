from flask import Flask, jsonify, request, send_file, Response, redirect, send_from_directory
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

@app.before_request
def validate_conversation():
    """验证会话ID有效性"""
    if request.method == 'POST' and '/conversations/' in request.path:
        path_segments = request.path.strip('/').split('/')
        # 确保路径结构正确：/api/conversations/{conv_id}/messages
        if len(path_segments) < 4 or path_segments[2] != 'conversations':
            return  # 忽略无效路径
        
        conv_id = path_segments[3]  # 正确提取会话ID位置
        
        if not db.session.get(Conversation, conv_id):
            return jsonify({
                "status": "error",
                "message": "无效的会话ID"
            }), 400

@app.route('/')
def index():
    """主入口返回前端页面"""
    return send_file('static/index.html')

@app.route('/<path:path>')
def static_files(path):
    """处理静态文件请求"""
    if path.startswith('static/'):
        return send_from_directory('.', path)
    return send_file('static/index.html')

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
            conv = Conversation(id=conversation_id)
            db.session.add(conv)
        else:
            # 检查会话是否存在且未过期
            conv = db.session.get(Conversation, conversation_id)
            if not conv or conv.last_active < (datetime.utcnow() - SESSION_EXPIRY):
                # 自动创建新会话
                conversation_id = str(uuid.uuid4())
                conv = Conversation(id=conversation_id)
                db.session.add(conv)
        
        # 更新最后活动时间
        conv.last_active = datetime.utcnow()
        
        # 获取历史消息
        messages = [msg.to_dict() for msg in conv.messages.order_by(
            Message.timestamp.desc()
        ).limit(9).all()][::-1]
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
        
        # 会话验证
        conv = db.session.get(Conversation, conversation_id)
        if not conv:
            return jsonify({
                "status": "error",
                "message": "无效的会话ID"
            }), 400
        
        # 更新会话时间
        conv.last_active = datetime.utcnow()
        
        # 保存用户消息
        user_msg = Message(
            conversation_id=conversation_id,
            role='user',
            content=user_message
        )
        db.session.add(user_msg)
        db.session.commit()

        def generate():
            with app.app_context():
                # 重新获取会话对象
                conv = db.session.get(Conversation, conversation_id)
                
                # 获取最近9条消息（正序查询）
                recent_messages = conv.messages.order_by(
                    Message.timestamp.desc()
                ).limit(9).all()
                
                # 反转顺序保持时间升序
                messages = [msg.to_dict() for msg in reversed(recent_messages)]
                messages.append({"role": "user", "content": user_message})
                
                # 确保会话对象已存在并提交
                db.session.add(conv)
                db.session.commit()  # 强制立即提交会话
                
                # 创建用户消息并提交
                user_msg = Message(conversation_id=conv.id, role='user', content=user_message)
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
                    ai_msg = Message(conversation_id=conv.id, role='assistant', content=''.join(full_response))
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
    conversation = db.session.get(Conversation, conversation_id)
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
    conversation = db.session.get(Conversation, conversation_id)
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
    conversation = db.session.get(Conversation, conversation_id)
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
                # 首行发送元数据
                yield json.dumps({
                    'conversation_id': conversation.id,
                    'created_at': conversation.created_at.isoformat(),
                    'last_active': conversation.last_active.isoformat()
                }) + '\n'
                
                # 分批处理消息
                query = Message.query.filter_by(
                    conversation_id=conversation_id
                ).yield_per(100)
                
                for msg in query:
                    yield json.dumps({
                        'timestamp': msg.timestamp.isoformat(),
                        'role': msg.role,
                        'content': msg.content
                    }, ensure_ascii=False) + '\n'
        
        headers = {
            'Content-Type': 'application/jsonl',
            'Content-Disposition': 
                f'attachment; filename=conversation_{conversation_id}.jsonl'
        }
        return Response(generate_json(), headers=headers)
    
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported format, use csv or json"
        }), 400

@app.route('/api/conversations/export-all', methods=['GET'])
def export_all_conversations():
    """支持完整消息导出的批量导出"""
    try:
        export_format = request.args.get('format', 'json')
        
        if export_format == 'csv':
            def generate_csv():
                with app.app_context():
                    mem = StringIO()
                    writer = csv.writer(mem)
                    
                    # 写入会话表头
                    writer.writerow([
                        '会话ID', '创建时间', '最后活跃时间', 
                        '消息数量', '第一条消息时间', '最后一条消息时间',
                        '用户消息数量', 'AI消息数量'
                    ])
                    yield mem.getvalue()
                    mem.seek(0)
                    mem.truncate(0)
                    
                    # 分批处理会话（每次50个）
                    conv_query = Conversation.query.yield_per(50)
                    for conv in conv_query:
                        # 统计消息信息
                        first_msg = db.session.query(
                            Message.timestamp
                        ).filter_by(
                            conversation_id=conv.id
                        ).order_by(Message.timestamp.asc()).first()
                        
                        last_msg = db.session.query(
                            Message.timestamp
                        ).filter_by(
                            conversation_id=conv.id
                        ).order_by(Message.timestamp.desc()).first()
                        
                        user_count = Message.query.filter_by(
                            conversation_id=conv.id,
                            role='user'
                        ).count()
                        
                        ai_count = Message.query.filter_by(
                            conversation_id=conv.id,
                            role='assistant'
                        ).count()
                        
                        # 写入会话数据
                        writer.writerow([
                            conv.id,
                            conv.created_at.isoformat(),
                            conv.last_active.isoformat(),
                            len(conv.messages),
                            first_msg[0].isoformat() if first_msg else '',
                            last_msg[0].isoformat() if last_msg else '',
                            user_count,
                            ai_count
                        ])
                        yield mem.getvalue()
                        mem.seek(0)
                        mem.truncate(0)
                        
                        # 写入消息明细
                        msg_query = Message.query.filter_by(
                            conversation_id=conv.id
                        ).yield_per(100)
                        for msg in msg_query:
                            writer.writerow([
                                '',  # 会话ID占位符
                                msg.timestamp.isoformat(),
                                msg.role,
                                msg.content.replace('\n', '\\n')
                            ])
                            yield mem.getvalue()
                            mem.seek(0)
                            mem.truncate(0)
            
            headers = {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=full_conversations_export_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
            }
            return Response(generate_csv(), headers=headers)
        
        elif export_format == 'json':
            def generate_json():
                with app.app_context():
                    # 首行元数据
                    yield json.dumps({
                        "export_time": datetime.now().isoformat(),
                        "total_conversations": Conversation.query.count()
                    }) + '\n'
                    
                    # 分批处理会话（每次50个会话）
                    conv_query = Conversation.query.yield_per(50)
                    for conv in conv_query:
                        # 分批加载消息（每次100条）
                        messages = []
                        msg_query = Message.query.filter_by(
                            conversation_id=conv.id
                        ).yield_per(100)
                        for msg in msg_query:
                            messages.append({
                                "timestamp": msg.timestamp.isoformat(),
                                "role": msg.role,
                                "content": msg.content
                            })
                        
                        # 构建完整会话数据
                        yield json.dumps({
                            "id": conv.id,
                            "created_at": conv.created_at.isoformat(),
                            "last_active": conv.last_active.isoformat(),
                            "message_count": len(messages),
                            "messages": messages  # 包含完整消息列表
                        }, ensure_ascii=False) + '\n'
            
            headers = {
                'Content-Type': 'application/x-ndjson',
                'Content-Disposition': f'attachment; filename=full_conversations_export_{datetime.now().strftime("%Y%m%d%H%M%S")}.ndjson'
            }
            return Response(generate_json(), headers=headers)
        
        else:
            return jsonify({
                "status": "error",
                "message": "不支持的导出格式，支持格式：csv, json"
            }), 400
        
    except Exception as e:
        app.logger.error(f"导出异常: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500
    
@app.route('/api/conversations')
def get_conversations():
    """获取会话列表"""
    try:
        conversations = Conversation.query.order_by(
            Conversation.last_active.desc()
        ).limit(50).all()
        
        return jsonify([{
            "id": conv.id,
            "last_active": conv.last_active.isoformat(),
            "message_count": conv.messages.count()
        } for conv in conversations])
        
    except Exception as e:
        app.logger.error(f"获取会话列表失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "获取会话列表失败"
        }), 500

@app.route('/api/new-conversation', methods=['POST'])
def create_conversation():
    """创建新会话"""
    try:
        conv_id = str(uuid.uuid4())
        conversation = Conversation(id=conv_id)
        db.session.add(conversation)
        db.session.commit()
        # 确保会话立即可查询
        db.session.expire_all()
        return jsonify({
            "status": "success",
            "conversation_id": conv_id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建会话失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "创建会话失败"
        }), 500

@app.route('/api/new-conversation', methods=['GET'])
def handle_invalid_new_conversation():
    """拦截错误的GET请求"""
    return jsonify({
        "status": "error",
        "message": "请使用POST方法创建新会话"
    }), 405

@app.route('/api/conversations/<conv_id>/messages', methods=['POST'])
def save_message(conv_id):
    """保存消息到会话"""
    try:
        data = request.json
        message = Message(
            conversation_id=conv_id,
            role=data['role'],
            content=data['content'],
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        app.logger.error(f"保存消息失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "保存消息失败"
        }), 500

# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True) 