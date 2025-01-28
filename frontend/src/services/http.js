import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import store from '../store'

const http = axios.create({
  baseURL: '/api',
  timeout: 5000
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    // 只返回响应数据部分
    return response.data
  },
  error => {
    // 统一错误处理
    const message = error.response?.data?.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default http 