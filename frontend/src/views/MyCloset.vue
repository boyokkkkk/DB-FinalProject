<template>
  <div class="my-closet">
    <div class="search-bar">
      <h1>My Closet</h1>
      <p class="welcome">Welcome back, get ready for your day.</p>
      <div class="search-container">
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          placeholder="Search items by name, color..." 
          class="search-input"
        />
        <button class="add-btn" @click="openAddModal()">
          + Add Item
        </button>
      </div>
    </div>

    <div v-if="!selectedCategory" class="categories-grid">
      <h2>All Categories</h2>
      <div class="categories">
        <div 
          v-for="category in categories" 
          :key="category.category_id"
          class="category-card"
          @click="selectCategory(category)"
        >
          <div class="category-icon">
            <span>{{ getCategoryEmoji(category.category_type) }}</span>
          </div>
          <h3>{{ category.category_name }}</h3>
          <p class="item-count">{{ category.item_count || 0 }} items</p>
        </div>
      </div>
      <div v-if="categories.length === 0" class="empty-state">
        暂无分类数据，请检查网络或登录状态。
      </div>
    </div>

    <div v-else class="clothes-grid">
      <div class="breadcrumb">
        <button class="back-btn" @click="selectedCategory = null">
          ← Back to Categories
        </button>
        <h2>{{ selectedCategory.category_name }}</h2>
        <p>{{ clothes.length }} items</p>
      </div>
      
      <div class="clothes">
        <div 
          v-for="item in clothes" 
          :key="item.item_id"
          class="clothing-card"
          @click="selectClothing(item)"
        >
          <div class="clothing-image">
            <img 
              :src="getImageUrl(item.image_url)" 
              :alt="item.name"
            />
          </div>
          <div class="clothing-info">
            <div class="brand">{{ item.brand }}</div>
            <h4>{{ item.name }}</h4>
            <div class="tags">
              <span v-if="item.season" class="tag season">{{ item.season }}</span>
              <span v-if="item.style" class="tag style">{{ item.style }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showClothingDetail" class="modal-overlay" @click="closeDetail">
      <div class="clothing-detail" @click.stop>
        <button class="close-btn" @click="closeDetail">×</button>
        <div class="detail-header">
          <img :src="getImageUrl(selectedClothing.image_url)" class="detail-image"/>
          <div class="detail-info">
            <div class="brand">{{ selectedClothing.brand }}</div>
            <h2>{{ selectedClothing.name }}</h2>
            <div class="detail-tags">
               <span class="tag">{{ selectedClothing.season }}</span>
               <span class="tag">{{ selectedClothing.style }}</span>
            </div>
          </div>
        </div>
        <div class="detail-content">
            <div class="detail-item"><span class="label">Material:</span> {{ selectedClothing.material }}</div>
            <div class="detail-item"><span class="label">Price:</span> {{ selectedClothing.price }}</div>
        </div>
        <div class="action-buttons">
          <button class="btn-edit" @click="editClothing">Edit</button>
          <button class="btn-delete" @click="deleteClothing">Delete</button>
        </div>
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="add-modal" @click.stop>
        <h2>{{ editingClothingId ? 'Edit Item' : 'Add New Item' }}</h2>
        <form @submit.prevent="saveClothing">
          <div class="form-grid">
            <div class="form-group">
              <label>Name</label><input v-model="formData.name" required />
            </div>
            <div class="form-group">
               <label>Category</label>
               <select v-model="formData.category_id" required>
                 <option v-for="c in categories" :key="c.category_id" :value="c.category_id">
                   {{ c.category_name }}
                 </option>
               </select>
            </div>
            <div class="form-group">
              <label>Image URL</label><input v-model="formData.image_url" placeholder="http://... or /static/..." />
            </div>
            </div>
          <div class="form-actions">
            <button type="button" @click="closeAddModal">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '../utils/request' // 为了分用户我加了这个

// 状态定义
const categories = ref([])
const clothes = ref([])
const selectedCategory = ref(null)
const selectedClothing = ref(null)
const showClothingDetail = ref(false)
const showAddModal = ref(false)
const searchQuery = ref('')
const editingClothingId = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  category_id: '',
  brand: '',
  color: '',
  season: '',
  style: '',
  material: '',
  price: null,
  image_url: '',
  notes: ''
})

const fetchCategories = async () => {
  try {
    // [修复] request 会自动带 Token
    const res = await request.get('/api/closet/categories') 
    
    // [修复] 直接用 res
    categories.value = res 
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const fetchClothesByCategory = async (categoryId) => {
  try {
    const res = await request.get(`/api/closet/category/${categoryId}`)
    clothes.value = res.clothes
  } catch (error) {
    console.error('获取衣物失败', error)
  }
}

const handleSearch = async () => {
  if (!searchQuery.value) return
  try {
    const res = await request.get('/api/closet/items/search', {
      params: { query: searchQuery.value }
    })
    
    // 这里简单处理：如果没选分类，就没有地方展示搜索结果列表，
    console.log('搜索结果', res)
  } catch (e) {}
}

const saveClothing = async () => {
  try {
    const payload = { ...formData }
    payload.price = payload.price ? parseFloat(payload.price) : null
    
    // 不再传递 user_id，后端会从 Token 获取
    if (editingClothingId.value) {
      await request.put(`/api/closet/items/${editingClothingId.value}`, payload)
    } else {
      await request.post('/api/closet/items', payload)
    }
    
    closeAddModal()
    if (selectedCategory.value) {
      fetchClothesByCategory(selectedCategory.value.category_id)
    }
    fetchCategories()
  } catch (error) {
    console.error(error)
  }
}

const deleteClothing = async () => {
  if(!confirm('确定删除?')) return
  try {
    await request.delete(`/api/closet/items/${selectedClothing.value.item_id}`)
    showClothingDetail.value = false
    if (selectedCategory.value) fetchClothesByCategory(selectedCategory.value.category_id)
    fetchCategories()
  } catch (e) {}
}


const selectCategory = (cat) => {
  selectedCategory.value = cat
  fetchClothesByCategory(cat.category_id)
}

const selectClothing = (item) => {
  selectedClothing.value = item
  showClothingDetail.value = true
}

const openAddModal = () => {
  editingClothingId.value = null
  resetForm()
  showAddModal.value = true
}

const editClothing = () => {
  editingClothingId.value = selectedClothing.value.item_id
  Object.assign(formData, selectedClothing.value)
  showClothingDetail.value = false
  showAddModal.value = true
}

const closeDetail = () => { showClothingDetail.value = false }
const closeAddModal = () => { showAddModal.value = false }

const resetForm = () => {
  Object.keys(formData).forEach(k => formData[k] = '')
  formData.price = null
}

const getCategoryEmoji = (type) => {
  const map = {
    'top': '👕', 'bottom': '👖', 'outerwear': '🧥',
    'dress': '👗', 'shoes': '👟', 'other': '👜'
  }
  return map[type] || '📦'
}

// 图片路径处理
const getImageUrl = (url) => {
  if (!url) return '/placeholder.png' // 这里的 placeholder 自己找个图或者删掉
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>

.my-closet { padding: 20px; font-family: 'Inter', sans-serif; }
.search-bar h1 { margin: 0 0 5px 0; color: #1e293b; }
.welcome { color: #64748b; margin-bottom: 20px; font-size: 14px; }
.search-container { display: flex; gap: 10px; margin-bottom: 30px; }
.search-input { flex: 1; padding: 10px 15px; border: 1px solid #cbd5e1; border-radius: 8px; }
.add-btn { background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }

.categories-grid h2 { margin-bottom: 20px; }
.categories { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.category-card { background: white; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; cursor: pointer; transition: 0.2s; }
.category-card:hover { border-color: #6366f1; transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.category-icon { font-size: 32px; margin-bottom: 10px; }
.item-count { color: #94a3b8; font-size: 12px; }

.clothes-grid .breadcrumb { display: flex; align-items: baseline; gap: 15px; margin-bottom: 20px; }
.back-btn { background: none; border: none; color: #6366f1; cursor: pointer; font-weight: 600; }
.clothes { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; }
.clothing-card { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; cursor: pointer; }
.clothing-image { height: 200px; background: #f8fafc; }
.clothing-image img { width: 100%; height: 100%; object-fit: cover; }
.clothing-info { padding: 10px; }
.clothing-info h4 { margin: 5px 0; font-size: 14px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 100; }
.clothing-detail, .add-modal { background: white; padding: 30px; border-radius: 12px; width: 500px; max-width: 90%; position: relative; }
.close-btn { position: absolute; top: 15px; right: 15px; border: none; background: none; font-size: 20px; cursor: pointer; }
.detail-header { display: flex; gap: 20px; margin-bottom: 20px; }
.detail-image { width: 120px; height: 160px; object-fit: cover; border-radius: 8px; background: #f1f5f9; }

.form-grid { display: grid; gap: 15px; margin: 20px 0; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group input, .form-group select { padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; }
.empty-state { color: #94a3b8; text-align: center; padding: 40px; }
</style>