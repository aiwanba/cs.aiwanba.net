import http from './http'

export default {
  async getCompanyList() {
    try {
      const response = await http.get('/api/company/list')
      return response
    } catch (error) {
      throw error
    }
  },
  
  async createCompany(data) {
    try {
      const response = await http.post('/api/company/create', data)
      return response
    } catch (error) {
      throw error
    }
  },
  
  async getCompanyDetail(id) {
    try {
      const response = await http.get(`/api/company/${id}`)
      return response
    } catch (error) {
      throw error
    }
  }
} 