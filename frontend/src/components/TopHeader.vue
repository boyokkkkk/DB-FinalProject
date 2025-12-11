<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInfo = ref({
  username: '访客',
  role: 'User',
  avatar: ''
})

// 初始化时读取本地存储
const loadUser = () => {
  const stored = localStorage.getItem('user_info')
  if (stored) {
    const parsed = JSON.parse(stored)
    userInfo.value = {
      ...parsed,
      role: '普通用户' // 因为数据库没有role字段，前端这里暂时写死或者根据逻辑判断
    }
  }
}

const goToSettings = () => {
  router.push('/settings')
}

onMounted(() => {
  loadUser()
})
</script>

<template>
  <header class="top-header">
    <div class="header-left">
      </div>

    <div class="header-right">
      <div class="user-info" @click="goToSettings" title="点击进入设置">
        <div class="text-info">
          <span class="name">{{ userInfo.username }}</span>
          <span class="role">{{ userInfo.role }}</span>
        </div>
        <img
          v-if="userInfo.avatar"
          :src="`http://127.0.0.1:8000${userInfo.avatar}`"
          class="avatar"
        />
        <div v-else class="avatar default-avatar">
          {{ userInfo.username.charAt(0).toUpperCase() }}
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-header {
  height: 80px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  background-color: transparent;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer; /* 鼠标变成手型 */
  padding: 5px 10px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: rgba(0,0,0,0.05); /* 悬停效果 */
}

.text-info {
  text-align: right;
}

.name {
  display: block;
  font-weight: bold;
  font-size: 14px;
  color: #333;
}

.role {
  font-size: 12px;
  color: #999;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.default-avatar {
  background-color: #6B69F6; /* 主题色 */
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}
</style>