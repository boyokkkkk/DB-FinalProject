<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request' // 引入刚才封装的工具

const router = useRouter()

// 定义表单数据
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    alert('请输入用户名和密码')
    return
  }

  try {
    // 发送 POST 请求给后端 /api/user/login
    const res = await request.post('/api/user/login', form.value)

    // 登录成功！
    console.log('登录成功:', res)

    // 1. 把用户信息存到浏览器本地 (LocalStorage)
    // 这样刷新页面后，还能记得你是谁
    localStorage.setItem('user_info', JSON.stringify(res.data))

    // 2. 跳转到主页 (Dashboard)
    alert('登录成功，欢迎回来！')
    router.push('/')

  } catch (error) {
    // 错误已经在 request.js 里弹窗了，这里不用管
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo">🧥</div>
      <h2>CLOSET OS</h2>
      <p class="subtitle">智能衣橱管理系统</p>

      <div class="form-group">
        <input
          v-model="form.username"
          type="text"
          placeholder="请输入用户名"
        />
      </div>

      <div class="form-group">
        <input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          @keyup.enter="handleLogin"
        />
      </div>

      <button @click="handleLogin" class="login-btn">登 录</button>

      <div class="footer-link">
        还没有账号？ <router-link to="/register">去注册</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 简单的卡片样式 */
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F2F3F5;
}

.login-box {
  width: 400px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  text-align: center;
}

.logo {
  font-size: 40px;
  margin-bottom: 10px;
}

h2 {
  margin: 0;
  color: #333;
}

.subtitle {
  color: #999;
  margin-bottom: 30px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #EEE;
  border-radius: 8px;
  box-sizing: border-box; /* 关键：防止输入框撑破容器 */
  outline: none;
  transition: 0.3s;
}

input:focus {
  border-color: #6B69F6;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #6B69F6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.login-btn:hover {
  background-color: #5a58d6;
}

.footer-link {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.footer-link a {
  color: #6B69F6;
  font-weight: bold;
}
</style>