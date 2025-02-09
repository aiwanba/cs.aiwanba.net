# API接口文档

## 基础信息
- **基准地址**: `https://cs.aiwanba.net`
- **响应格式**: JSON
- 错误代码：
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

**响应**：直接返回文件下载

### 6. 批量导出会话
**URL** `/api/conversations/export-all`  
**方法** GET  
**参数**：
- `start_date`: 起始日期（ISO格式）
- `end_date`: 结束日期
- `format`: json/csv

**响应**：ZIP压缩包包含所有会话数据

## 系统状态

### 7. 服务健康检查
**URL** `/health`  
**方法** GET  
**响应**：
```json
{
  "status": "正常",
  "version": "1.0.0"
}
```

## 使用示例

### 普通聊天请求
```bash
curl -X POST https://cs.aiwanba.net/api/chat \
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
