<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    alert('请填写完整信息')
    return
  }
  if (form.value.password !== form.value.confirmPassword) {
    alert('两次输入的密码不一致！')
    return
  }

  try {
    // 调用后端的注册接口
    await request.post('/api/user/register', {
      username: form.value.username,
      password: form.value.password
    })

    alert('注册成功！请登录')
    router.push('/login') // 跳回登录页

  } catch (error) {
    // 错误处理交给了 request.js
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <div class="logo">🧥</div>
      <h2>创建新账号</h2>
      <p class="subtitle">加入 Closet OS</p>

      <div class="form-group">
        <input v-model="form.username" type="text" placeholder="设置用户名" />
      </div>

      <div class="form-group">
        <input v-model="form.password" type="password" placeholder="设置密码" />
      </div>

      <div class="form-group">
        <input
          v-model="form.confirmPassword"
          type="password"
          placeholder="确认密码"
          @keyup.enter="handleRegister"
        />
      </div>

      <button @click="handleRegister" class="reg-btn">注 册</button>

      <div class="footer-link">
        已有账号？ <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 复用大部分 Login 的样式，简单改一下背景色以示区分 */
.register-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #6B69F6; /* 用紫色背景区分注册页 */
}

.register-box {
  width: 400px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  text-align: center;
}

.logo { font-size: 40px; margin-bottom: 10px; }
h2 { margin: 0; color: #333; }
.subtitle { color: #999; margin-bottom: 30px; font-size: 14px; }
.form-group { margin-bottom: 20px; }

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #EEE;
  border-radius: 8px;
  box-sizing: border-box;
  outline: none;
}
input:focus { border-color: #6B69F6; }

.reg-btn {
  width: 100%;
  padding: 12px;
  background-color: #333; /* 黑色按钮 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.footer-link { margin-top: 20px; font-size: 14px; color: #666; }
.footer-link a { color: #6B69F6; font-weight: bold; }
</style>