let currentConversationId = null;
let isStreaming = false;

// 初始化加载会话列表
window.onload = () => {
    loadConversationHistory();
};

async function sendMessage() {
    if (isStreaming) return;
    
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage('user', message);
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

// 其他JS函数保持不变... 