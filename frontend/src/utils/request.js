// src/utils/request.js
import axios from 'axios'

// 1. 创建 axios 实例
const service = axios.create({
  // 后端接口的基础地址 (FastAPI 默认是 8000)
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000 // 请求超时时间 (5秒)
})

// 2. 请求拦截器 (比如发送请求前如果要带 Token，就在这里处理)
service.interceptors.request.use(
  config => {
    let token = localStorage.getItem('token') 
    
    if (!token) {
        const userInfo = localStorage.getItem('user_info')
        if (userInfo) {
            try {
                token = JSON.parse(userInfo).token
            } catch (e) {}
        }
    }

    // 如果有 token，加到 Header 里
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 3. 响应拦截器 (统一处理报错)
service.interceptors.response.use(
  response => {
    // 如果后端返回 200，直接把数据拿出来
    return response.data
  },
  error => {
    // 如果报错 (比如 401, 500)，在这里弹窗提示
    console.error('请求出错:', error)
    alert('请求失败: ' + (error.response?.data?.detail || error.message))
    return Promise.reject(error)
  }
)

export default service