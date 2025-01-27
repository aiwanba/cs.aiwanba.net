import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)

  const connect = () => {
    const token = localStorage.getItem('token')
    if (!token) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws?token=${token}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      isConnected.value = true
      console.log('WebSocket连接已建立')
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }

    ws.value.onclose = () => {
      isConnected.value = false
      console.log('WebSocket连接已关闭')
      // 尝试重新连接
      setTimeout(connect, 3000)
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket错误:', error)
      ws.value.close()
    }
  }

  const disconnect = () => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.close()
    }
  }

  const handleMessage = (data) => {
    switch (data.type) {
      case 'system':
      case 'trade':
        ElMessage({
          message: data.content,
          type: data.type === 'system' ? 'warning' : 'success',
          duration: 5000
        })
        break
      default:
        console.log('未处理的消息类型:', data.type)
    }
  }

  return {
    isConnected,
    connect,
    disconnect
  }
} 