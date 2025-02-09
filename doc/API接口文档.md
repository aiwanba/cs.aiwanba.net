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
  "response": "建议从Python语言开始学习...",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "cached": false
}
```

### 流式对话
**POST /api/chat-stream**  
（使用Server-Sent Events协议）
```bash
curl -X POST http://localhost:5010/api/chat-stream \
  -H "Content-Type: application/json" \
  -d '{"message":"请介绍人工智能"}'
```
实时响应示例：
```
data: {"content": "人工"}
data: {"content": "智能"}
data: {"content": "是..."}
```

## 会话管理接口

### 获取会话历史
**GET /api/conversations/{conversation_id}**  
```bash
curl http://localhost:5010/api/conversations/550e8400-e29b-41d4-a716-446655440000
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
curl -X DELETE http://localhost:5010/api/conversations/550e8400-e29b-41d4-a716-446655440000
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