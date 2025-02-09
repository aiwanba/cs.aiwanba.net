from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from openai import OpenAI
from functools import lru_cache
import uuid
from models import db, Conversation, Message
from apscheduler.schedulers.background import BackgroundScheduler
import csv
from io import StringIO
import json
import httpx

app = Flask(__name__)
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

@app.route('/')
def index():
    return jsonify({
        "status": "成功",
        "message": "服务器正在运行",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "正常",
        "version": "1.0.0"
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
            conversation = Conversation.query.get(conversation_id)
            if not conversation:
                return jsonify({
                    "status": "error",
                    "message": "Conversation not found"
                }), 404
        
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
        
        # 调用API获取响应
        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=4096
        )
        
        # 获取AI响应
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        
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
        
        # 如果没有会话ID，创建新的会话
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(id=conversation_id)
            db.session.add(conversation)
        else:
            conversation = Conversation.query.get(conversation_id)
            if not conversation:
                return jsonify({
                    "status": "error",
                    "message": "Conversation not found"
                }), 404
        
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
        
        # 创建生成器流式响应
        def generate():
            completion = client.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=messages,
                temperature=1,
                top_p=1,
                max_tokens=4096,
                stream=True  # 启用流式模式
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

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
            "status": "error",
            "message": "Conversation not found"
        }), 404
    
    db.session.delete(conversation)
    db.session.commit()
    
    # 清除相关缓存
    for key in list(response_cache.keys()):
        if key.startswith(f"{conversation_id}:"):
            del response_cache[key]
    
    return jsonify({
        "status": "success",
        "message": "Conversation history cleared"
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
        
        # 创建内存文件
        mem = StringIO()
        json.dump(data, mem, indent=2, ensure_ascii=False)
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
        # 创建CSV内存文件
        mem = StringIO()
        writer = csv.writer(mem)
        
        # 写入头部
        writer.writerow(['Timestamp', 'Role', 'Content'])
        
        # 写入消息
        for message in conversation.messages:
            writer.writerow([
                message.timestamp.isoformat(),
                message.role,
                message.content
            ])
        
        mem.seek(0)
        
        # 生成文件名
        filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported export format"
        }), 400

@app.route('/api/conversations/export-all', methods=['GET'])
def export_all_conversations():
    """导出所有会话数据"""
    # 获取时间范围参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    export_format = request.args.get('format', 'json')
    
    # 构建查询
    query = Conversation.query
    
    if start_date:
        query = query.filter(Conversation.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Conversation.created_at <= datetime.fromisoformat(end_date))
    
    conversations = query.all()
    
    if export_format == 'json':
        # 准备JSON数据
        data = {
            'export_date': datetime.now().isoformat(),
            'conversations': [{
                'conversation_id': conv.id,
                'created_at': conv.created_at.isoformat(),
                'last_active': conv.last_active.isoformat(),
                'messages': [msg.to_dict() for msg in conv.messages]
            } for conv in conversations]
        }
        
        # 创建内存文件
        mem = StringIO()
        json.dump(data, mem, indent=2, ensure_ascii=False)
        mem.seek(0)
        
        # 生成文件名
        filename = f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    
    elif export_format == 'csv':
        # 创建CSV内存文件
        mem = StringIO()
        writer = csv.writer(mem)
        
        # 写入头部
        writer.writerow(['Conversation ID', 'Timestamp', 'Role', 'Content'])
        
        # 写入所有会话的消息
        for conv in conversations:
            for message in conv.messages:
                writer.writerow([
                    conv.id,
                    message.timestamp.isoformat(),
                    message.role,
                    message.content
                ])
        
        mem.seek(0)
        
        # 生成文件名
        filename = f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported export format"
        }), 400

# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True) 