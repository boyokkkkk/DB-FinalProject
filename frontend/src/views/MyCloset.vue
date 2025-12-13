<template>
  <div class="my-closet">
    <!-- 顶部搜索栏 -->
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
        <button class="add-btn" @click="showAddModal = true">
          + Add Item
        </button>
      </div>
    </div>

    <!-- 分类卡片网格 -->
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
    </div>

    <!-- 衣物列表 -->
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
              :src="item.image_url || '/placeholder-clothing.png'" 
              :alt="item.name"
            />
          </div>
          <div class="clothing-info">
            <div class="brand">{{ item.brand }}</div>
            <h4>{{ item.name }}</h4>
            <div class="tags">
              <span v-if="item.season" class="tag season">{{ item.season }}</span>
              <span v-if="item.style" class="tag style">{{ item.style }}</span>
              <span v-if="item.color" class="tag color">{{ item.color }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 衣物详情模态框 -->
    <div v-if="showClothingDetail" class="modal-overlay" @click="closeDetail">
      <div class="clothing-detail" @click.stop>
        <button class="close-btn" @click="closeDetail">×</button>
        
        <div class="detail-header">
          <img 
            :src="selectedClothing.image_url || '/placeholder-clothing.png'" 
            :alt="selectedClothing.name"
            class="detail-image"
          />
          <div class="detail-info">
            <div class="brand">{{ selectedClothing.brand }}</div>
            <h2>{{ selectedClothing.name }}</h2>
            <div class="detail-tags">
              <span v-if="selectedClothing.season" class="tag">{{ selectedClothing.season }}</span>
              <span v-if="selectedClothing.style" class="tag">{{ selectedClothing.style }}</span>
              <span v-if="selectedClothing.color" class="tag">{{ selectedClothing.color }}</span>
            </div>
          </div>
        </div>

        <div class="detail-content">
          <div class="detail-section">
            <h3>Details</h3>
            <div class="details-grid">
              <div class="detail-item">
                <span class="label">Material:</span>
                <span>{{ selectedClothing.material || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Purchase Date:</span>
                <span>{{ formatDate(selectedClothing.purchase_date) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Price:</span>
                <span>{{ selectedClothing.price ? `$${selectedClothing.price}` : 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Added:</span>
                <span>{{ formatDate(selectedClothing.created_at) }}</span>
              </div>
            </div>
          </div>

          <div v-if="selectedClothing.notes" class="detail-section">
            <h3>Notes</h3>
            <p>{{ selectedClothing.notes }}</p>
          </div>

          <div class="action-buttons">
            <button class="btn-edit" @click="editClothing">Edit</button>
            <button class="btn-delete" @click="deleteClothing">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑衣物模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="add-modal" @click.stop>
        <h2>{{ editingClothing ? 'Edit Item' : 'Add New Item' }}</h2>
        
        <form @submit.prevent="saveClothing">
          <div class="form-grid">
            <div class="form-group">
              <label>Name *</label>
              <input v-model="newClothing.name" required />
            </div>
            
            <div class="form-group">
              <label>Brand</label>
              <input v-model="newClothing.brand" />
            </div>
            
            <div class="form-group">
              <label>Category *</label>
              <select v-model="newClothing.category_id" required>
                <option value="">Select Category</option>
                <option 
                  v-for="cat in categories" 
                  :key="cat.category_id" 
                  :value="cat.category_id"
                >
                  {{ cat.category_name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Color</label>
              <input v-model="newClothing.color" />
            </div>
            
            <div class="form-group">
              <label>Season</label>
              <select v-model="newClothing.season">
                <option value="">Select Season</option>
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
                <option value="Autumn">Autumn</option>
                <option value="Winter">Winter</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Style</label>
              <input v-model="newClothing.style" />
            </div>
            
            <div class="form-group">
              <label>Material</label>
              <input v-model="newClothing.material" />
            </div>
            
            <div class="form-group">
              <label>Price</label>
              <input v-model="newClothing.price" type="number" step="0.01" />
            </div>
            
            <div class="form-group">
              <label>Purchase Date</label>
              <input v-model="newClothing.purchase_date" type="date" />
            </div>
            
            <div class="form-group full-width">
              <label>Image URL</label>
              <input v-model="newClothing.image_url" />
            </div>
            
            <div class="form-group full-width">
              <label>Notes</label>
              <textarea v-model="newClothing.notes" rows="3"></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeAddModal">Cancel</button>
            <button type="submit">{{ editingClothing ? 'Update' : 'Add' }} Item</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'

// 响应式数据
const categories = ref([])
const clothes = ref([])
const selectedCategory = ref(null)
const selectedClothing = ref(null)
const showClothingDetail = ref(false)
const showAddModal = ref(false)
const searchQuery = ref('')
const editingClothing = ref(null)

const newClothing = reactive({
  user_id: 1,
  name: '',
  brand: '',
  category_id: '',
  color: '',
  season: '',
  style: '',
  material: '',
  price: null,
  purchase_date: '',
  image_url: '',
  notes: ''
})

// 生命周期钩子
onMounted(() => {
  fetchCategories()
})

// API调用
const fetchCategories = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/closet/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchClothesByCategory = async (categoryId) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/closet/category/${categoryId}`)
    clothes.value = response.data.clothes
  } catch (error) {
    console.error('Failed to fetch clothes:', error)
  }
}

const searchClothes = async () => {
  try {
    const params = {}
    if (searchQuery.value) params.query = searchQuery.value
    if (selectedCategory.value) params.category_id = selectedCategory.value.category_id
    
    const response = await axios.get('http://localhost:8000/api/closet/items/search', { params })
    clothes.value = response.data
  } catch (error) {
    console.error('Failed to search clothes:', error)
  }
}

// 事件处理
const selectCategory = (category) => {
  selectedCategory.value = category
  fetchClothesByCategory(category.category_id)
}

const selectClothing = (item) => {
  selectedClothing.value = item
  showClothingDetail.value = true
}

const closeDetail = () => {
  showClothingDetail.value = false
  selectedClothing.value = null
}

const handleSearch = () => {
  if (!selectedCategory.value) return
  searchClothes()
}

const getCategoryEmoji = (type) => {
  const emojis = {
    'top': '👕',
    'bottom': '👖',
    'outerwear': '🧥',
    'dress': '👗',
    'shoes': '👟',
    'other': '👜'
  }
  return emojis[type] || '👚'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const editClothing = () => {
  editingClothing.value = selectedClothing.value.item_id
  Object.assign(newClothing, {
    ...selectedClothing.value,
    purchase_date: selectedClothing.value.purchase_date 
      ? new Date(selectedClothing.value.purchase_date).toISOString().split('T')[0]
      : ''
  })
  showClothingDetail.value = false
  showAddModal.value = true
}

const deleteClothing = async () => {
  if (!confirm('Are you sure you want to delete this item?')) return
  
  try {
    await axios.delete(`http://localhost:8000/api/closet/items/${selectedClothing.value.item_id}`)
    showClothingDetail.value = false
    if (selectedCategory.value) {
      fetchClothesByCategory(selectedCategory.value.category_id)
    }
  } catch (error) {
    console.error('Failed to delete clothing:', error)
  }
}

const saveClothing = async () => {
  try {
    const clothingData = {
      ...newClothing,
      user_id: newClothing.user_id || 1,  // 确保有值
      purchase_date: newClothing.purchase_date || null,
    }

    if (editingClothing.value) {
      await axios.put(
        `http://localhost:8000/api/closet/items/${editingClothing.value}`,
        newClothing
      )
    } else {
      await axios.post('http://localhost:8000/api/closet/items', newClothing)
    }
    
    closeAddModal()
    if (selectedCategory.value) {
      fetchClothesByCategory(selectedCategory.value.category_id)
    } else {
      fetchCategories()
    }
  } catch (error) {
    console.error('Failed to save clothing:', error)
    console.error('错误详情:', error.response?.data)
  }
}

const closeAddModal = () => {
  showAddModal.value = false
  editingClothing.value = null
  const currentUserId = newClothing.user_id
  Object.keys(newClothing).forEach(key => {
    newClothing[key] = ''
  })
  newClothing.user_id = currentUserId || 1
}
</script>

<style scoped>
.my-closet {
  padding: 20px;
}

.search-bar {
  margin-bottom: 30px;
}

.welcome {
  color: #666;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 15px;
  max-width: 600px;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
}

.add-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.categories-grid h2 {
  margin-bottom: 20px;
}

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.category-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.category-card:hover {
  transform: translateY(-5px);
  border-color: #4f46e5;
  box-shadow: 0 5px 20px rgba(79, 70, 229, 0.1);
}

.category-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.item-count {
  color: #666;
  font-size: 14px;
}

.clothes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.clothing-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.clothing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.clothing-image {
  height: 180px;
  overflow: hidden;
}

.clothing-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.clothing-card:hover .clothing-image img {
  transform: scale(1.05);
}

.clothing-info {
  padding: 15px;
}

.brand {
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 5px;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.tag.season {
  background: #e0f2fe;
  color: #0369a1;
}

.tag.style {
  background: #fef3c7;
  color: #92400e;
}

.tag.color {
  background: #f1f5f9;
  color: #475569;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.clothing-detail {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.detail-header {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.detail-image {
  width: 250px;
  height: 300px;
  object-fit: cover;
  border-radius: 12px;
}

.detail-info {
  flex: 1;
}

.detail-section {
  margin-bottom: 25px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.label {
  font-weight: 500;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-edit, .btn-delete {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-edit {
  background: #4f46e5;
  color: white;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.add-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 25px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.form-actions button {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.form-actions button[type="submit"] {
  background: #4f46e5;
  color: white;
}

.breadcrumb {
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  color: #4f46e5;
  cursor: pointer;
  padding: 0;
  margin-bottom: 10px;
  font-size: 14px;
}

.back-btn:hover {
  text-decoration: underline;
}
</style>