<template>
  <div class="my-closet">
    <!-- 顶部搜索栏 -->
    <div class="search-bar">
      <h1>My Closet</h1>
      <p class="welcome">Welcome back, get ready for your day.</p>
      <div class="search-container">
        <div class="search-input-wrapper">
          <input
            v-model="searchQuery"
            @input="handleSearchDebounced"
            @keyup.enter="handleSearchImmediate"
            placeholder="Search items by name, brand, color, tags..."
            class="search-input"
          />
          <!-- 新增：加载中图标 -->
          <span v-if="isSearching" class="search-loading">🔄</span>
        </div>
        <button class="add-btn" @click="openAddModal()">
          + Add Item
        </button>
      </div>
      <!-- 搜索清空按钮 -->
      <button
        v-if="searchQuery || filterCategory || filterColor || filterSeason || filterOccasion"
        class="clear-search-btn"
        @click="clearAllFilters"
      >
        Clear All
      </button>
      <!-- 新增：搜索反馈提示 -->
      <div v-if="searchFeedback" class="search-feedback">
        {{ searchFeedback }}
      </div>
    </div>

    <!-- 筛选器栏（新增occasion） -->
    <div class="filters-bar" v-if="!selectedCategory">
      <div class="filter-row">
        <div class="filter-group">
          <label>Category:</label>
          <select v-model="filterCategory" @change="handleFilterChange">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
              {{ cat.category_name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>Color:</label>
          <input
            v-model="filterColor"
            @input="handleFilterChange"
            placeholder="e.g. Red, Black"
            class="filter-input"
          />
        </div>
        <div class="filter-group">
          <label>Season:</label>
          <select v-model="filterSeason" @change="handleFilterChange">
            <option value="">All Seasons</option>
            <option value="Spring">Spring</option>
            <option value="Summer">Summer</option>
            <option value="Autumn">Autumn</option>
            <option value="Winter">Winter</option>
            <option value="All Seasons">All Seasons</option>
          </select>
        </div>
        <!-- 新增：Occasion筛选器 -->
        <div class="filter-group">
          <label>Occasion:</label>
          <input
            v-model="filterOccasion"
            @input="handleFilterChange"
            placeholder="e.g. Casual, Formal"
            class="filter-input"
          />
        </div>
      </div>
    </div>

    <!-- 筛选结果展示 -->
    <div v-if="(searchQuery || filterCategory || filterColor || filterSeason || filterOccasion) && !selectedCategory" class="search-results-section">
      <div class="breadcrumb">
        <h2>
          {{ searchQuery ? `Search Results for "${searchQuery}"` : "Filtered Results" }}
        </h2>
        <p>{{ filteredResults.length }} item(s) found</p>
      </div>

      <!-- 新增：加载中占位 -->
      <div v-if="isSearching" class="loading-state">
        Loading items...
      </div>

      <div v-else class="clothes">
        <div
          v-for="item in filteredResults"
          :key="item.item_id"
          class="clothing-card"
          @click="selectClothing(item)"
        >
          <div class="clothing-image">
            <img
              :src="getImageUrl(item.image_url)"
              :alt="item.name"
              crossorigin="anonymous"
            />
          </div>

          <div class="clothing-info">
            <div class="brand">{{ item.brand }}</div>
            <h4>{{ item.name }}</h4>
            <div class="tags">
              <span v-if="item.season" class="tag season">{{ item.season }}</span>
              <span v-if="item.color" class="tag color">{{ item.color }}</span>
              <span v-if="item.style" class="tag style">{{ item.style }}</span>
              <span v-if="item.occasion" class="tag occasion">{{ item.occasion }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 无结果提示（优化文案） -->
      <div v-if="!isSearching && filteredResults.length === 0" class="empty-state">
        {{ searchQuery ? `No items found matching "${searchQuery}"` : "No items match your filters" }}
        <br/>Try adjusting your search terms or filters.
      </div>
    </div>

    <!-- 分类卡片网格 -->
    <div v-if="!searchQuery && !filterCategory && !filterColor && !filterSeason && !filterOccasion && !selectedCategory" class="categories-grid">
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

    <!-- 分类下的衣物列表 -->
    <div v-if="selectedCategory" class="clothes-grid">
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
              <span v-if="item.color" class="tag color">{{ item.color }}</span>
              <span v-if="item.style" class="tag style">{{ item.style }}</span>
              <span v-if="item.occasion" class="tag occasion">{{ item.occasion }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分类下无数据提示 -->
      <div v-if="clothes.length === 0" class="empty-state">
        No items in this category yet. Add your first item!
      </div>
    </div>

    <!-- 衣物详情模态框 -->
    <div v-if="showClothingDetail" class="modal-overlay" @click="closeDetail">
      <div class="clothing-detail" @click.stop>
        <button class="close-btn" @click="closeDetail">×</button>
        <div class="detail-header">
          <img :src="getImageUrl(selectedClothing.image_url)" class="detail-image"/>
          <div class="detail-info">
            <div class="brand">{{ selectedClothing.brand || 'No brand' }}</div>
            <h2>{{ selectedClothing.name }}</h2>
            <div class="detail-tags">
               <span class="tag season" v-if="selectedClothing.season">{{ selectedClothing.season }}</span>
               <span class="tag color" v-if="selectedClothing.color">{{ selectedClothing.color }}</span>
               <span class="tag style" v-if="selectedClothing.style">{{ selectedClothing.style }}</span>
               <span class="tag occasion" v-if="selectedClothing.occasion">{{ selectedClothing.occasion }}</span>
            </div>
          </div>
        </div>
        <div class="detail-content">
          <div class="detail-item"><span class="label">Category:</span> {{ getCategoryName(selectedClothing.category_id) }}</div>
          <div class="detail-item"><span class="label">Material:</span> {{ selectedClothing.material || 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Purchase Date:</span> {{ formatDate(selectedClothing.purchase_date) || 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Price:</span> {{ selectedClothing.price ? '$' + selectedClothing.price.toFixed(2) : 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Occasion:</span> {{ selectedClothing.occasion || 'Not specified' }}</div>
          <div class="detail-item full-width">
            <span class="label">Notes:</span>
            <div class="notes-content">{{ selectedClothing.notes || 'No notes' }}</div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn-edit" @click="editClothing">Edit</button>
          <button class="btn-delete" @click="deleteClothing">Delete</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑衣物模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="add-modal" @click.stop>
        <h2>{{ editingClothingId ? 'Edit Item' : 'Add New Item' }}</h2>
        <form @submit.prevent="saveClothing">
          <div class="form-grid">
            <div class="form-group">
              <label>Name *</label>
              <input v-model="formData.name" required />
            </div>
            <div class="form-group">
              <label>Category *</label>
              <select v-model="formData.category_id" required>
                <option value="">Select category</option>
                <option v-for="c in categories" :key="c.category_id" :value="c.category_id">
                  {{ c.category_name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Brand</label>
              <input v-model="formData.brand" placeholder="e.g. Nike, Zara" />
            </div>
            <div class="form-group">
              <label>Color</label>
              <input v-model="formData.color" placeholder="e.g. Blue, Black" />
            </div>
            <div class="form-group">
              <label>Season</label>
              <select v-model="formData.season">
                <option value="">Select season</option>
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
                <option value="Autumn">Autumn</option>
                <option value="Winter">Winter</option>
                <option value="All Seasons">All Seasons</option>
              </select>
            </div>
            <div class="form-group">
              <label>Occasion</label>
              <input v-model="formData.occasion" placeholder="e.g. Casual, Formal" />
            </div>
            <div class="form-group">
              <label>Style</label>
              <input v-model="formData.style" placeholder="e.g. Minimalist, Vintage" />
            </div>
            <div class="form-group">
              <label>Material</label>
              <input v-model="formData.material" placeholder="e.g. Cotton, Polyester" />
            </div>
            <div class="form-group">
              <label>Purchase Date</label>
              <input v-model="formData.purchase_date" type="date" />
            </div>
            <div class="form-group">
              <label>Price ($)</label>
              <input v-model="formData.price" type="number" step="0.01" min="0" />
            </div>
            <div class="form-group full-width">
              <label>Image</label>
              <input v-model="formData.image_url" placeholder="http://... or /static/..." />
            </div>
            <div class="form-group full-width">
              <label>Notes</label>
              <textarea v-model="formData.notes" rows="4" placeholder="Add any additional notes..."></textarea>
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
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../utils/request'

// 核心状态定义
const categories = ref([])
const clothes = ref([])
const selectedCategory = ref(null)
const selectedClothing = ref(null)
const showClothingDetail = ref(false)
const showAddModal = ref(false)
const searchQuery = ref('')
const editingClothingId = ref(null)
const allItems = ref([])
const searchInitiated = ref(false)

// 新增：搜索状态相关
const isSearching = ref(false) // 是否正在搜索
const searchFeedback = ref('') // 搜索反馈提示
let searchDebounceTimer = null // 防抖计时器

// 筛选器状态（新增filterOccasion）
const filterCategory = ref('')
const filterColor = ref('')
const filterSeason = ref('')
const filterOccasion = ref('') // 新增：场合筛选

// 筛选结果计算（新增occasion筛选逻辑）
const filteredResults = computed(() => {
  let results = [...allItems.value]

  // 1. 搜索词筛选
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    results = results.filter(item =>
      item.name?.toLowerCase().includes(keyword) ||
      item.brand?.toLowerCase().includes(keyword) ||
      item.color?.toLowerCase().includes(keyword) ||
      item.season?.toLowerCase().includes(keyword) ||
      item.style?.toLowerCase().includes(keyword) ||
      item.occasion?.toLowerCase().includes(keyword) // 新增：搜索词匹配occasion
    )
  }

  // 2. 筛选器筛选
  if (filterCategory.value) {
    results = results.filter(item => item.category_id == filterCategory.value)
  }
  if (filterColor.value.trim()) {
    const color = filterColor.value.trim().toLowerCase()
    results = results.filter(item => item.color?.toLowerCase().includes(color))
  }
  if (filterSeason.value) {
    results = results.filter(item => item.season === filterSeason.value)
  }
  // 新增：occasion筛选逻辑
  if (filterOccasion.value.trim()) {
    const occasion = filterOccasion.value.trim().toLowerCase()
    results = results.filter(item => item.occasion?.toLowerCase().includes(occasion))
  }

  return results
})

// 表单数据
const formData = reactive({
  name: '',
  category_id: '',
  brand: '',
  color: '',
  season: '',
  occasion: '',
  style: '',
  material: '',
  purchase_date: '',
  price: null,
  image_url: '',
  notes: ''
})

// 分类名称映射
const categoryMap = computed(() => {
  return categories.value.reduce((map, category) => {
    map[category.category_id] = category.category_name
    return map
  }, {})
})

// 获取全量物品数据（新增加载状态）
const fetchAllItems = async (isManualSearch = false) => {
  if (isManualSearch) {
    isSearching.value = true
    searchFeedback.value = 'Searching for items...'
  }
  try {
    const res = await request.get('/api/closet/items/search')
    allItems.value = res.data || res
    if (isManualSearch) {
      searchFeedback.value = `Found ${allItems.value.length} total items`
      // 3秒后隐藏反馈
      setTimeout(() => {
        searchFeedback.value = ''
      }, 3000)
    }
  } catch (error) {
    console.error('获取全量物品失败', error)
    allItems.value = []
    if (isManualSearch) {
      searchFeedback.value = 'Failed to load items, please try again'
    }
  } finally {
    if (isManualSearch) {
      isSearching.value = false
    }
  }
}

// 获取分类
const fetchCategories = async () => {
  try {
    const res = await request.get('/api/closet/categories')
    categories.value = res
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

// 获取分类下物品
const fetchClothesByCategory = async (categoryId) => {
  try {
    const res = await request.get(`/api/closet/category/${categoryId}`)
    clothes.value = res.clothes || res
  } catch (error) {
    console.error('获取衣物失败', error)
    clothes.value = []
  }
}

// 新增：防抖搜索（输入停止500ms后执行）
const handleSearchDebounced = () => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    handleSearchImmediate()
  }, 500)
}

// 新增：立即搜索（回车/防抖后执行）
const handleSearchImmediate = () => {
  if (!searchQuery.value.trim() && !filterCategory.value && !filterColor.value && !filterSeason.value && !filterOccasion.value) {
    searchFeedback.value = ''
    return
  }
  searchInitiated.value = true
  // 重新请求最新数据（确保和后端同步）
  fetchAllItems(true)
}

// 筛选器变化触发（新增加载反馈）
const handleFilterChange = () => {
  searchInitiated.value = true
  isSearching.value = true
  searchFeedback.value = 'Applying filters...'
  // 筛选是本地操作，立即结束加载
  setTimeout(() => {
    isSearching.value = false
    searchFeedback.value = `Filtered to ${filteredResults.value.length} items`
    setTimeout(() => {
      searchFeedback.value = ''
    }, 2000)
  }, 300)
}

// 清空所有筛选/搜索
const clearAllFilters = () => {
  searchQuery.value = ''
  filterCategory.value = ''
  filterColor.value = ''
  filterSeason.value = ''
  filterOccasion.value = '' // 新增：清空occasion筛选
  selectedCategory.value = null
  searchInitiated.value = false
  searchFeedback.value = 'Filters cleared'
  setTimeout(() => {
    searchFeedback.value = ''
  }, 2000)
}

// 选择分类
const selectCategory = (cat) => {
  selectedCategory.value = cat
  fetchClothesByCategory(cat.category_id)
  // 清空筛选器
  filterCategory.value = ''
  filterColor.value = ''
  filterSeason.value = ''
  filterOccasion.value = '' // 新增：清空occasion筛选
  searchQuery.value = ''
  searchInitiated.value = false
  searchFeedback.value = ''
}

// 保存衣物
const saveClothing = async () => {
  try {
    const payload = {
        ...formData,
        occasion: formData.occasion.trim() || null,
        color: formData.color.trim() || null,
        season: formData.season || null,
        purchase_date: formData.purchase_date || null
     }
    payload.price = payload.price ? parseFloat(payload.price) : null

    if (editingClothingId.value) {
      const res = await request.put(`/api/closet/items/${editingClothingId.value}`, payload)
      console.log('更新响应:', res)
    } else {
      await request.post('/api/closet/items', payload)
    }

    closeAddModal()

    // 保存后刷新数据
    setTimeout(async () => {
      fetchAllItems()
      if (selectedCategory.value) {
        fetchClothesByCategory(selectedCategory.value.category_id)
      }
      fetchCategories()
    }, 300)

    alert(editingClothingId.value ? 'Item updated successfully!' : 'Item added successfully!')
  } catch (error) {
    console.error('保存失败详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      payload: formData
    })
    alert('Failed to save item: ' + (error.response?.data?.detail || error.message))
  }
}

// 删除衣物
const deleteClothing = async () => {
  if(!confirm('确定删除该物品?')) return

  try {
    await request.delete(`/api/closet/items/${selectedClothing.value.item_id}`)
    showClothingDetail.value = false

    // 删除后刷新数据
    fetchAllItems()
    if (selectedCategory.value) {
      fetchClothesByCategory(selectedCategory.value.category_id)
    }
    fetchCategories()
  } catch (e) {
    console.error('删除失败', e)
    alert('Failed to delete item: ' + (e.response?.data?.detail || e.message))
  }
}

// 其他方法
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
  if (selectedClothing.value.purchase_date) {
    const date = new Date(selectedClothing.value.purchase_date)
    formData.purchase_date = date.toISOString().split('T')[0]
  }
  Object.assign(formData, {
    ...selectedClothing.value,
    price: selectedClothing.value.price ? Number(selectedClothing.value.price) : null
  })
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

const getImageUrl = (url) => {
  if (!url) return '/placeholder.png'
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}

const getCategoryName = (categoryId) => {
  return categoryMap.value[categoryId] || 'Unknown'
}

const formatDate = (dateString) => {
  if (!dateString) return null
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 初始化
onMounted(() => {
  fetchCategories()
  fetchAllItems()
})
</script>

<style scoped>
.my-closet {
  padding: 20px;
  font-family: 'Inter', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

/* 搜索栏样式 */
.search-bar h1 { margin: 0 0 5px 0; color: #1e293b; }
.welcome { color: #64748b; margin-bottom: 10px; font-size: 14px; }
.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
/* 新增：搜索输入框容器（包含加载图标） */
.search-input-wrapper {
  flex: 1;
  min-width: 200px;
  position: relative;
}
.search-input {
  width: 90%;
  padding: 12px 15px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  padding-right: 40px; /* 给加载图标留空间 */
}
/* 新增：加载中图标 */
.search-loading {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #6366f1;
}
/* 新增：搜索反馈提示 */
.search-feedback {
  font-size: 12px;
  color: #64748b;
  margin: 5px 0;
  font-style: italic;
}
.add-btn {
  white-space: nowrap;
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}
.clear-search-btn {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 20px;
}
.clear-search-btn:hover {
  background: #e2e8f0;
}

/* 筛选器栏样式（适配新增的occasion） */
.filters-bar {
  margin: 15px 0;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
}
.filter-row {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 160px;
  flex: 1;
  max-width: 220px;
}
.filter-group label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}
.filter-group select, .filter-input {
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  width: 100%;
}

/* 分类网格样式 */
.categories-grid h2 { margin-bottom: 20px; }
.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
.category-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: 0.2s;
}
.category-card:hover {
  border-color: #6366f1;
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.category-icon { font-size: 32px; margin-bottom: 10px; }
.item-count { color: #94a3b8; font-size: 12px; }

/* 面包屑样式 */
.breadcrumb {
  display: flex;
  align-items: baseline;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.back-btn {
  background: none;
  border: none;
  color: #6366f1;
  cursor: pointer;
  font-weight: 600;
}
.breadcrumb h2 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
}
.breadcrumb p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* 新增：加载状态样式 */
.loading-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
  font-size: 14px;
}

/* 衣物网格样式 */
.clothes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}
.clothing-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: 0.2s;
}
.clothing-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.clothing-image {
  height: 200px;
  background-color: #ffffff; /* 确保背景是纯白，而不是透明显示出的底层黑影 */
  display: flex;
  align-items: center;
  justify-content: center;
}
.clothing-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 确保透明 PNG 不会被拉伸变形 */
  background: transparent; /* 强制图片本身背景透明 */
}
.clothing-info {
  padding: 10px;
}
.clothing-info h4 {
  margin: 5px 0;
  font-size: 14px;
}
.clothing-info .brand {
  color: #64748b;
  font-size: 12px;
}

.el-image {
  background-color: #fff; /* 确保图片加载前或透明区域是白色的 */
}

/* 标签样式 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
}
.tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}
.tag.season { background: #dbeafe; color: #1e40af; }
.tag.color { background: #fef3c7; color: #92400e; }
.tag.style { background: #dcfce7; color: #065f46; }
.tag.occasion { background: #fee2e2; color: #991b1b; }

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}
.clothing-detail, .add-modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 600px;
  max-width: 90%;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}
.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}
.detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.detail-image {
  width: 120px;
  height: 160px;
  object-fit: cover;
  border-radius: 8px;
  background: #f1f5f9;
}
.detail-info .brand {
  color: #64748b;
  margin-bottom: 5px;
}
.detail-tags { margin-top: 10px; }

/* 详情内容样式 */
.detail-content {
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}
.detail-item { display: flex; flex-direction: column; }
.detail-item.full-width { grid-column: 1 / -1; }
.label {
  font-weight: 600;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 3px;
}
.notes-content {
  white-space: pre-line;
  background: #f8fafc;
  padding: 10px;
  border-radius: 6px;
}

/* 表单样式 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 20px 0;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-group.full-width { grid-column: 1 / -1; }
.form-group label {
  font-weight: 500;
  font-size: 13px;
  color: #334155;
}
.form-group input, .form-group select, .form-group textarea {
  padding: 8px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-family: inherit;
}
.form-group textarea { resize: vertical; }
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
.form-actions button {
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
.form-actions button[type="button"] {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}
.form-actions button[type="submit"] {
  background: #6366f1;
  color: white;
  border: none;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}
.btn-edit {
  background: #6366f1;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
.btn-delete {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

/* 空状态样式 */
.empty-state {
  color: #94a3b8;
  text-align: center;
  padding: 40px;
  font-size: 14px;
}

/* 搜索结果区域样式 */
.search-results-section {
  margin-top: 20px;
}
</style>