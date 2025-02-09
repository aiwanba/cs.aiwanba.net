# API 接口文档

## 基础服务接口

### 服务状态检查
**GET /**  
```bash
curl http://localhost:5010/
```
响应示例：
```json
{
  "status": "success",
  "message": "Server is running",
  "timestamp": "2024-03-21 15:30:45"
}
```

### 健康检查
**GET /health**  
```bash
curl http://localhost:5010/health
```
响应示例：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 智能对话接口

### 普通对话
**POST /api/chat**  
请求格式：
```json
{
  "message": "你的问题",
  "conversation_id": "可选会话ID"
}
```
示例请求：
```bash
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"如何学习编程？"}'
```
响应示例：
```json
{
  "status": "success",
  "response": "您好！很高兴为您服务。请问有什么可以帮助您的？",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "cached": false
}
```

注意事项：
1. 响应内容可能包含Markdown格式（如**粗体**、`代码块`等）
2. 换行符保持AI生成的原样格式
3. 中文标点符号遵循AI生成习惯

### 流式对话
**POST /api/chat-stream**  
响应特性：
1. 使用UTF-8编码，避免Unicode转义字符
2. 自动过滤Markdown格式符号
3. 保持自然中文标点

示例响应：
```
data: {"content": "人工"}
data: {"content": "智能"}
data: {"content": "是..."}
```

## 会话管理接口

### 获取会话历史
**GET /api/conversations/{conversation_id}**  
```bash
curl http://localhost:5010/api/conversations/a1e5f35e-2f8f-4641-be9d-94311d549e02
```
响应示例：
```json
{
  "status": "success",
  "history": [
    {
      "role": "user",
      "content": "如何学习编程？",
      "timestamp": "2024-03-21T15:30:45"
    },
    {
      "role": "assistant", 
      "content": "建议从Python语言开始学习...",
      "timestamp": "2024-03-21T15:30:46"
    }
  ]
}
```

### 删除会话
**DELETE /api/conversations/{conversation_id}**  
```bash
curl -X DELETE http://localhost:5010/api/conversations/a1e5f35e-2f8f-4641-be9d-94311d549e02
```
响应示例：
```json
{
  "status": "success",
  "message": "Conversation history cleared"
}
```

## 数据导出接口

### 导出单个会话
**GET /api/conversations/{conversation_id}/export**  
参数：
- `format`: json/csv

```bash
curl -o output.json http://localhost:5010/api/conversations/550e8400-e29b-41d4-a716-446655440000/export?format=json
```

### 批量导出会话
**GET /api/conversations/export-all**  
参数：
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD 
- `format`: json/csv

```bash
curl -o all.csv http://localhost:5010/api/conversations/export-all?start_date=2024-03-01&end_date=2024-03-21&format=csv
```

## 注意事项
1. 生产环境请使用HTTPS
2. 流式接口需要前端配合处理SSE协议
3. 会话ID有效期24小时
4. 相同问题会返回缓存响应（标注cached:true） 