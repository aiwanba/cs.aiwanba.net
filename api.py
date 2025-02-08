from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
import urllib3
import json
from datetime import datetime

# 禁用不安全的 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# 存储对话历史
conversations = []

def create_client():
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        stream = data.get('stream', False)
        
        # 记录对话历史
        conversation_id = len(conversations)
        conversation = {
            'id': conversation_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'messages': []
        }
        
        # 添加用户消息
        conversation['messages'].append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        client = create_client()
        
        if stream:
            def generate():
                completion = client.chat.completions.create(
                    model="deepseek-ai/deepseek-r1",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6,
                    top_p=0.7,
                    max_tokens=4096,
                    stream=True
                )
                
                full_response = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                
                # 保存AI响应到对话历史
                conversation['messages'].append({
                    'role': 'assistant',
                    'content': full_response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                conversations.append(conversation)
                
            return Response(generate(), mimetype='text/event-stream')
        else:
            completion = client.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                top_p=0.7,
                max_tokens=4096,
                stream=False
            )
            
            response = completion.choices[0].message.content
            
            # 保存AI响应到对话历史
            conversation['messages'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            conversations.append(conversation)
            
            return jsonify({"success": True, "response": response})
                
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history')
def get_history():
    return jsonify(conversations)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5010, debug=True) 