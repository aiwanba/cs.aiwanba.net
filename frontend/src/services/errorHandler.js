import { ElMessage } from 'element-plus'

// 错误码映射
const ERROR_CODES = {
  400: '请求参数错误',
  401: '未登录或登录已过期',
  403: '没有操作权限',
  404: '请求的资源不存在',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '网关超时'
}

// API错误处理
export const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response
    
    // 处理特定状态码
    if (status === 401) {
      // 清除登录信息
      localStorage.removeItem('token')
      // 跳转到登录页
      window.location.href = '/login'
      return
    }

    // 显示错误消息
    ElMessage.error(data.message || ERROR_CODES[status] || '请求失败')
  } else if (error.request) {
    // 请求发出但没有收到响应
    ElMessage.error('网络连接失败，请检查网络设置')
  } else {
    // 请求配置出错
    ElMessage.error('请求配置错误')
  }
}

// 业务错误处理
export const handleBusinessError = (code, message) => {
  switch (code) {
    case 'INSUFFICIENT_BALANCE':
      ElMessage.error('账户余额不足')
      break
    case 'EXCEED_LIMIT':
      ElMessage.error('超出限额')
      break
    case 'INVALID_OPERATION':
      ElMessage.error(message || '操作无效')
      break
    default:
      ElMessage.error(message || '操作失败')
  }
}

// WebSocket错误处理
export const handleWebSocketError = (error) => {
  console.error('WebSocket错误:', error)
  ElMessage.error('实时连接异常，正在尝试重新连接...')
}

// 表单验证错误处理
export const handleValidationError = (fields) => {
  const errors = Object.values(fields)
    .filter(field => field.length > 0)
    .map(field => field[0].message)
  
  ElMessage.error(errors[0] || '表单验证失败')
} 