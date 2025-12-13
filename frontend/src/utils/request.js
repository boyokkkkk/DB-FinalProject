import axios from 'axios';

// 先安装axios：npm install axios
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  timeout: 5000 // 请求超时时间
});

// 响应拦截器：统一处理返回值
request.interceptors.response.use(
  (res) => {
    // 只返回接口的data部分，简化前端调用
    return res.data;
  },
  (err) => {
    console.error('请求失败：', err.message);
    // 统一错误提示（可选）
    alert('网络异常，请稍后重试');
    return Promise.reject(err);
  }
);

export default request;