import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import mock from './mock'

// 判断是否静态托管环境（GitHub Pages 等无后端环境）
const isStaticHost = () => {
  const host = window.location.hostname
  return host.endsWith('.github.io') || host.includes('vercel.app') || host.includes('netlify.app') || host === 'localhost' && !localStorage.getItem('api_base')
}

// 全局切换：api_mode = 'mock' | 'real'
const apiMode = () => {
  if (localStorage.getItem('api_mode') === 'real') return 'real'
  return isStaticHost() ? 'mock' : 'real'
}

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.request.use(config => {
  // Mock 模式直接走演示数据
  if (apiMode() === 'mock') {
    config._mock = true
    return config
  }
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  async response => {
    if (response.config._mock) return response.data
    return response.data
  },
  error => {
    if (error.config?._mock) {
      return mock.route(error.config).then(r => r.data)
    }
    const status = error.response?.status
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      const msg = error.response?.data?.detail || error.message || '请求失败'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

// Mock 模式：所有请求直接返回演示数据（不真正发请求，避免 404）
const realRequest = api.request.bind(api)
api.request = config => {
  if (apiMode() === 'mock') {
    return mock.route({
      method: (config.method || 'get').toLowerCase(),
      url: config.url || '',
      params: config.params || {},
      data: config.data || null
    }).then(r => r.data)
  }
  return realRequest(config)
}
// 兼容 get/post/put/delete 快捷方法
;['get', 'post', 'put', 'delete', 'patch'].forEach(m => {
  const origin = api[m].bind(api)
  api[m] = (url, config = {}) => {
    if (apiMode() === 'mock') {
      return mock.route({
        method: m,
        url,
        params: config.params || {},
        data: config.data || (m !== 'get' && m !== 'delete' ? config : null)
      }).then(r => r.data)
    }
    return origin(url, config)
  }
})

export default api
