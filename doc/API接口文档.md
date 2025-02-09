# API接口文档

## 基础信息
- **基准地址**: `https://cs.aiwanba.net` 和 `http://localhost:5010`
- **响应格式**: JSON
- **错误代码**：
  - 200 成功
  - 400 请求参数错误
  - 404 资源未找到
  - 500 服务器内部错误

## 会话管理

### 1. 创建/继续聊天
**URL** `/api/chat`  
**方法** POST  
**请求体**：
```json
{
  "message": "用户消息内容",
  "conversation_id": "可选，已有会话ID"
}
```
**成功响应**：
```json
{
  "status": "success",
  "response": "AI回复内容",
  "conversation_id": "会话ID",
  "cached": "是否使用缓存"
}
```

### 2. 流式聊天
**URL** `/api/chat-stream`  
**方法** POST  
**请求体**：同普通聊天接口  
**响应格式**：Event Stream  
**数据示例**：
```
data: {"content": "部分响应内容"}
```

## 会话历史

### 3. 获取会话记录
**URL** `/api/conversations/{conversation_id}`  
**方法** GET  
**成功响应**：
```json
{
  "status": "success",
  "history": [
    {
      "role": "user/assistant",
      "content": "消息内容",
      "timestamp": "ISO时间"
    }
  ]
}
```

### 4. 删除会话
**URL** `/api/conversations/{conversation_id}`  
**方法** DELETE  
**成功响应**：
```json
{
  "status": "成功",
  "message": "会话历史已清除"
}
```

## 数据导出

### 5. 导出单个会话
**URL** `/api/conversations/{conversation_id}/export`  
**方法** GET  
**参数**：
- `format`: json/csv（默认json）

**响应**：
- CSV：流式文本数据
- JSON：流式JSON格式（每100条消息更新一次）

**特殊说明**：
- CSV导出支持10万+消息的流式处理
- 自动分批加载数据（每批100条消息）
- JSON格式适合实时处理大数据量

### 6. 批量导出会话
**URL** `/api/conversations/export-all`  
**方法** GET  
**参数**：
- `format`: json/csv（默认json）

**特殊说明**：
- JSON格式包含完整消息历史
- 采用双层分批加载机制（50会话/批 + 100消息/批）
- 内存优化设计，支持大规模数据导出

**响应示例**：
```json
{
  "export_time": "2025-02-10T09:30:00.000000",
  "total_conversations": 3587
}
{
  "id": "abc123",
  "created_at": "2024-05-28T10:00:00",
  "last_active": "2024-05-30T14:25:00",
  "message_count": 2,
  "messages": [
    {
      "timestamp": "2024-05-28T10:01:00", 
      "role": "user",
      "content": "美国历史"
    },
    {
      "timestamp": "2024-05-28T10:01:05",
      "role": "assistant", 
      "content": "美国历史概况..."
    }
  ]
}
```

## 系统状态

### 7. 服务健康检查
**URL** `/health`  
**方法** GET  
**响应**：
```json
{
  "status": "服务正常",
  "timestamp": "当前时间（格式：YYYY-MM-DD HH:MM:SS）",
  "system": {
    "database": "数据库连接状态",
    "cache": "当前缓存数量",
    "active_sessions": "活跃会话数量"
  }
}
```

## 使用示例

### 普通聊天请求
```bash
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

### 流式聊天请求
```javascript
const eventSource = new EventSource('/api/chat-stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};
```

### 健康检查
```bash
curl http://localhost:5010/health
```

## 注意事项
1. 会话ID有效期24小时，过期自动清理
2. 流式接口响应需要前端处理Event Stream格式
3. 导出文件默认保存时间为10分钟
