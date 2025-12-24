import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000
})

// 请求拦截器：每次请求自动带上 Token
service.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      // 按照 OAuth2 标准，Header 格式为 "Bearer <token>"
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理 401 未登录
service.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      // Token 过期或未登录
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token') // 清除失效 token
      
      // 强制跳转到登录页 (假设你配置了路由)
      // 如果没有路由，可以使用 window.location.href = '/login'
      window.location.href = '/login'
    } else {
      ElMessage.error(error.response?.data?.detail || '网络请求错误')
    }
    return Promise.reject(error)
  }
)

export default service