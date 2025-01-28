import http from './http'

export default {
  async getSummary() {
    try {
      const response = await http.get('/api/dashboard/summary')
      return response
    } catch (error) {
      throw error
    }
  }
} 