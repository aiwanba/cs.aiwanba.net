import http from './http'

export default {
  async register(data) {
    try {
      const response = await http.post('/auth/register', data)
      return response
    } catch (error) {
      throw error
    }
  },
  
  async login(data) {
    try {
      const response = await http.post('/auth/login', data)
      return response
    } catch (error) {
      throw error
    }
  }
} 