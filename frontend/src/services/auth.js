import http from './http'

export default {
  async register(data) {
    try {
      const response = await http.post('/api/auth/register', data)
      return response
    } catch (error) {
      throw error
    }
  },
  
  async login(data) {
    try {
      const response = await http.post('/api/auth/login', data)
      return response
    } catch (error) {
      throw error
    }
  }
} 