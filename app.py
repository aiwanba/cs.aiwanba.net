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
    """导出会话数据"""
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({
            "status": "error",
            "message": "Conversation not found"
        }), 404
    
    export_format = request.args.get('format', 'json')  # 支持 json 和 csv 格式
    
    if export_format == 'json':
        # 准备JSON数据
        data = {
            'conversation_id': conversation.id,
            'created_at': conversation.created_at.isoformat(),
            'last_active': conversation.last_active.isoformat(),
            'messages': [msg.to_dict() for msg in conversation.messages]
        }
        
        # 创建内存文件（二进制模式）
        mem = BytesIO()  # 改为使用BytesIO
        mem.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
        mem.seek(0)
        
        # 生成文件名
        filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    
    elif export_format == 'csv':
        # 创建CSV内存文件（二进制模式）
        mem = BytesIO()
        try:
            # 直接使用TextIOWrapper包装BytesIO
            wrapper = TextIOWrapper(mem, 'utf-8', newline='', write_through=True)
            writer = csv.writer(wrapper)
            
            # 写入头部
            writer.writerow(['Timestamp', 'Role', 'Content'])
            
            # 写入消息
            for message in conversation.messages:
                writer.writerow([
                    message.timestamp.isoformat(),
                    message.role,
                    message.content
                ])
            
            # 刷新缓冲区并重置指针
            wrapper.flush()
            mem.seek(0)
            
            # 生成文件名
            filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return send_file(
                mem,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        finally:
            # 仅关闭BytesIO对象
            mem.close()
    
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported export format"
        }), 400

@app.route('/api/conversations/export-all', methods=['GET'])
def export_all_conversations():
    try:
        # 参数解析和验证
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export_format = request.args.get('format', 'json')

        # 日期格式验证
        try:
            start_date = datetime.fromisoformat(start_date) if start_date else None
            end_date = datetime.fromisoformat(end_date) if end_date else None
        except ValueError as e:
            app.logger.error(f"日期格式错误: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "日期格式应为YYYY-MM-DD"
            }), 400

        # 构建查询
        query = Conversation.query
        if start_date:
            query = query.filter(Conversation.created_at >= start_date)
        if end_date:
            query = query.filter(Conversation.created_at <= end_date)

        conversations = query.all()

        # CSV导出处理
        if export_format == 'csv':
            import tempfile
            import shutil
            
            try:
                # 创建临时目录（自动清理）
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 生成临时文件路径
                    temp_path = os.path.join(temp_dir, 'export.csv')
                    
                    # 写入CSV文件
                    with open(temp_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        
                        # 写入表头
                        writer.writerow(['会话ID', '创建时间', '最后活跃时间', '消息数量'])
                        
                        # 写入数据
                        for conv in conversations:
                            writer.writerow([
                                conv.id,
                                conv.created_at.isoformat(),
                                conv.last_active.isoformat(),
                                len(conv.messages)
                            ])
                    
                    # 发送文件并自动清理
                    return send_file(
                        temp_path,
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f"conversations_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
                        conditional=True
                    )
                    
            except Exception as e:
                app.logger.error(f"CSV导出失败: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": "文件生成失败"
                }), 500

        # JSON导出处理
        elif export_format == 'json':
            # 准备JSON数据
            data = {
                'count': len(conversations),
                'conversations': [
                    {
                        'id': conv.id,
                        'created_at': conv.created_at.isoformat(),
                        'last_active': conv.last_active.isoformat(),
                        'message_count': len(conv.messages)
                    } for conv in conversations
                ]
            }
            
            # 创建内存文件（二进制模式）
            mem = BytesIO()
            mem.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
            mem.seek(0)
            
            # 生成文件名
            filename = f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return send_file(
                mem,
                mimetype='application/json',
                as_attachment=True,
                download_name=filename
            )
        
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
    
# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True) 