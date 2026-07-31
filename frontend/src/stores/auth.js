import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: state => !!state.token,
    isAdmin: state => state.user?.role_type === 'admin' || state.user?.is_superuser
  },
  actions: {
    async login(username, password) {
      const data = await api.post('/auth/login', { username, password })
      this.token = data.token
      this.user = data.user
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },
    async register(username, password, email, promoter = '') {
      // promoter 参数：0.01 元体验包经推广海报注册（走 /promotion/register）
      if (promoter) {
        const data = await api.post('/promotion/register', { username, password, email, promoter })
        this.token = data.token
        this.user = data.user || { username, plan: 'trial' }
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        if (data.orderId) localStorage.setItem('trialOrderId', data.orderId)
        return data
      }
      const data = await api.post('/auth/register', { username, password, email })
      this.token = data.token
      this.user = data.user
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    },
    async fetchProfile() {
      const data = await api.get('/auth/profile')
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
