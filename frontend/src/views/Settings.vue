<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { VueCropper } from 'vue-cropper/next'
import 'vue-cropper/next/dist/index.css'

const router = useRouter()
const fileInput = ref(null)

// 表单数据
const form = ref({
  user_id: null,
  username: '',
  password: '',
  avatar: ''
})

// === 裁剪相关状态 ===
const showCropper = ref(false) // 是否显示裁剪弹窗
const cropperImg = ref('')     // 待裁剪图片的 Base64
const cropper = ref(null)      // 裁剪组件的引用
const fileName = ref('')       // 原始文件名

onMounted(() => {
  const stored = localStorage.getItem('user_info')
  if (stored) {
    const parsed = JSON.parse(stored)
    form.value.user_id = parsed.user_id
    form.value.username = parsed.username
    form.value.avatar = parsed.avatar || ''
  }
})

// 1. 用户点击头像 -> 触发文件选择
const triggerUpload = () => {
  fileInput.value.click()
}

// 2. 文件选择后 -> 读取图片并显示裁剪弹窗 (不直接上传)
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 限制大小 (例如 5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB')
    return
  }

  fileName.value = file.name // 记住文件名

  // 使用 FileReader 读取图片为 Base64，传给裁剪组件
  const reader = new FileReader()
  reader.onload = (e) => {
    cropperImg.value = e.target.result // 设置给 cropper
    showCropper.value = true           // 打开弹窗
  }
  reader.readAsDataURL(file)

  // 清空 input，防止选同一张图不触发 change
  event.target.value = ''
}

// 3. 用户点击“确认裁剪” -> 生成 Blob 并上传
const confirmCrop = () => {
  // 获取裁剪后的数据 (Blob)
  cropper.value.getCropBlob(async (blob) => {
    // 构造 FormData
    const formData = new FormData()
    // 把 blob 当作文件传进去，第三个参数是文件名
    formData.append('file', blob, fileName.value)

    try {
      const res = await request.post(`/api/user/${form.value.user_id}/avatar`, formData)

      alert('头像更新成功！')
      form.value.avatar = res.avatar
      localStorage.setItem('user_info', JSON.stringify(res))

      // 关闭弹窗
      showCropper.value = false
      // 刷新页面让顶栏也更新
      window.location.reload()

    } catch (error) {
      console.error(error)
      alert('上传失败')
    }
  })
}

// 取消裁剪
const cancelCrop = () => {
  showCropper.value = false
  cropperImg.value = ''
}

// 保存基本信息
const handleSave = async () => {
  if (!form.value.user_id) return
  try {
    const updateData = { username: form.value.username }
    if (form.value.password) updateData.password = form.value.password
    const res = await request.put(`/api/user/${form.value.user_id}`, updateData)
    localStorage.setItem('user_info', JSON.stringify(res))
    alert('基本信息保存成功！')
    window.location.reload()
  } catch (error) {}
}

const handleLogout = () => {
  if(confirm('确定要退出登录吗？')) {
    localStorage.removeItem('user_info')
    router.push('/login')
  }
}
</script>

<template>
  <div class="settings-container">
    <div class="settings-card">
      <h2>个人设置</h2>
      <p class="subtitle">管理您的账户信息</p>

      <div class="avatar-section">
        <div class="avatar-wrapper" @click="triggerUpload">
          <img
            v-if="form.avatar"
            :src="`http://127.0.0.1:8000${form.avatar}`"
            class="avatar-img"
          />
          <div v-else class="avatar-placeholder">
            {{ form.username ? form.username.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div class="upload-mask">
            <span>更换头像</span>
          </div>
        </div>
        <input
          type="file"
          ref="fileInput"
          accept="image/*"
          style="display: none"
          @change="handleFileChange"
        />
      </div>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="form.username" type="text" />
      </div>
      <div class="form-group">
        <label>新密码 (选填)</label>
        <input v-model="form.password" type="password" placeholder="" />
      </div>
      <div class="actions">
        <button class="btn save-btn" @click="handleSave">保存信息</button>
        <button class="btn logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <div v-if="showCropper" class="cropper-modal">
      <div class="cropper-content">
        <h3>调整头像区域</h3>
        <div class="cropper-box">
          <vue-cropper
            ref="cropper"
            :img="cropperImg"
            :outputSize="0.8"
            :outputType="'png'"
            :autoCrop="true"
            :autoCropWidth="200"
            :autoCropHeight="200"
            :fixed="true"
            :fixedNumber="[1, 1]"
            :centerBox="true"
          ></vue-cropper>
        </div>
        <div class="cropper-actions">
          <button class="btn cancel-btn" @click="cancelCrop">取消</button>
          <button class="btn save-btn" @click="confirmCrop">确认并上传</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.settings-container {
  padding: 40px;
  display: flex;
  justify-content: center;
}
.settings-card {
  width: 500px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
h2 { margin: 0; color: #333; }
.subtitle { color: #999; font-size: 14px; margin-bottom: 30px; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: bold; }
input { width: 100%; padding: 12px; border: 1px solid #EEE; border-radius: 8px; outline: none; transition: 0.3s; box-sizing: border-box; }
input:focus { border-color: #6B69F6; }

/* 按钮通用 */
.btn { flex: 1; padding: 12px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; transition: 0.2s; }
.save-btn { background-color: #6B69F6; color: white; }
.save-btn:hover { background-color: #5a58d6; }
.logout-btn { background-color: #F7F8FA; color: #FF4D4F; }
.logout-btn:hover { background-color: #FFF1F0; }
.cancel-btn { background-color: #eee; color: #666; }
.cancel-btn:hover { background-color: #ddd; }

.actions { display: flex; gap: 15px; margin-top: 30px; }

/* 头像部分 */
.avatar-section { display: flex; justify-content: center; margin-bottom: 30px; }
.avatar-wrapper { width: 100px; height: 100px; border-radius: 50%; position: relative; cursor: pointer; overflow: hidden; border: 2px solid #EEE; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder { width: 100%; height: 100%; background-color: #FDC072; color: white; display: flex; justify-content: center; align-items: center; font-size: 36px; font-weight: bold; }
.upload-mask { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); color: white; display: flex; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s; font-size: 12px; }
.avatar-wrapper:hover .upload-mask { opacity: 1; }

/* === 裁剪弹窗样式 === */
.cropper-modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
}
.cropper-content {
  background: white;
  width: 500px;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}
.cropper-box {
  width: 100%;
  height: 400px; /* 裁剪区高度 */
  margin: 20px 0;
  background: #333;
}
.cropper-actions {
  display: flex;
  gap: 15px;
}
</style>