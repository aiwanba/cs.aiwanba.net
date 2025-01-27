import http from './http'

export const authService = {
  async login(username, password) {
    const response = await http.post('/api/auth/login', {
      username,
      password
    })
    return response
  },

  async register(data) {
    const response = await http.post('/api/auth/register', data)
    return response
  }
} 