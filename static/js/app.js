let currentConversationId = null;
let isStreaming = false;

// 初始化加载会话列表
window.onload = () => {
    loadConversationHistory();
};

// 消息处理函数
function addMessage(role, content) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="timestamp">${new Date().toLocaleTimeString()}</div>
    `;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 回车键处理
function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 加载会话历史（示例实现）
async function loadConversationHistory() {
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '请求失败');
        }
        
        const data = await response.json();
        const historyList = document.getElementById('historyList');
        
        // 清空现有列表
        historyList.innerHTML = '';
        
        // 渲染会话列表
        data.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.onclick = () => loadConversationMessages(conv.id);
            item.innerHTML = `
                <div class="conv-id">${conv.id.slice(0,6)}...</div>
                <div class="conv-info">
                    <span>${new Date(conv.last_active).toLocaleString()}</span>
                    <span>消息数：${conv.message_count}</span>
                </div>
            `;
            historyList.appendChild(item);
        });
        
    } catch (error) {
        console.error('加载历史记录失败:', error);
        showError(`加载失败: ${error.message}`);
    }
}

// 创建消息容器
function createMessageContainer(role) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-content"></div>
        <div class="timestamp"></div>
    `;
    messagesDiv.appendChild(messageDiv);
    return messageDiv;
}

// 添加时间戳
function addTimestamp(messageDiv) {
    const time = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
    messageDiv.querySelector('.timestamp').textContent = time;
}

// 获取会话ID
async function fetchConversationId() {
    try {
        const response = await fetch('/api/new-conversation', {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`HTTP错误 ${response.status}: ${error}`);
        }
        const data = await response.json();
        return data.conversation_id;
    } catch (error) {
        console.error('获取会话ID失败:', error);
        showError('无法创建新会话，请检查网络连接');
        return null;
    }
}

async function sendMessage() {
    if (isStreaming) return;
    
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    // 创建新会话
    if (!currentConversationId) {
        try {
            const response = await fetch('/api/new-conversation', {
                method: 'POST'
            });
            const data = await response.json();
            currentConversationId = data.conversation_id;
        } catch (error) {
            showError('创建会话失败');
            return;
        }
    }

    // 保存用户消息
    await saveMessage(currentConversationId, 'user', message);
    
    // 改用新消息容器
    const messageDiv = createMessageContainer('user');
    messageDiv.querySelector('.message-content').textContent = message;
    addTimestamp(messageDiv);
    
    input.value = '';
    
    document.getElementById('loading').style.display = 'block';
    isStreaming = true;

    try {
        const response = await fetch('/api/chat-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                conversation_id: currentConversationId
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        const messageDiv = createMessageContainer('assistant');

        while(true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            aiResponse += chunk;
            messageDiv.querySelector('.message-content').textContent = aiResponse;
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }

        currentConversationId = await fetchConversationId();

    } catch (error) {
        console.error('发送失败:', error);
        showError('请求失败，请检查网络');
        messageDiv.querySelector('.message-content').textContent = '⚠️ 请求失败';
    } finally {
        document.getElementById('loading').style.display = 'none';
        isStreaming = false;
        addTimestamp(messageDiv);
    }
}

async function saveMessage(convId, role, content) {
    try {
        await fetch(`/api/conversations/${convId}/messages`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ role, content })
        });
    } catch (error) {
        console.error('保存消息失败:', error);
    }
}

async function loadConversationMessages(convId) {
    try {
        const response = await fetch(`/api/conversations/${convId}/messages`);
        const messages = await response.json();
        
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = '';
        
        messages.forEach(msg => {
            const messageDiv = createMessageContainer(msg.role);
            messageDiv.querySelector('.message-content').textContent = msg.content;
            messageDiv.querySelector('.timestamp').textContent = 
                new Date(msg.timestamp).toLocaleTimeString();
        });
        
    } catch (error) {
        showError('加载消息失败');
    }
}

// 显示错误提示
function showError(message, duration=3000) {
    const toast = document.getElementById('errorToast');
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, duration);
}

// 其他JS函数保持不变... 