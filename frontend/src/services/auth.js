import http from './http'

export default {
  async register(data) {
    const response = await http.post('/auth/register', data)
    return response.data
  },
  
  async login(data) {
    const response = await http.post('/auth/login', data)
    return response.data
  }
} 