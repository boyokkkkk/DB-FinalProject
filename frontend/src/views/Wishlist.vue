<template>
  <div class="wishlist">
    <!-- 头部区域 -->
    <div class="header">
      <h1>My Wishlist</h1>
      <p class="subtitle">Keep track of clothes you want to add to your closet</p>

      <!-- 统计信息 -->
      <div class="stats-bar" v-if="stats">
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_items }}</span>
          <span class="stat-label">Total Items</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.added_to_closet }}</span>
          <span class="stat-label">Added to Closet</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.not_added }}</span>
          <span class="stat-label">Not Added</span>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="Search wishlist items..."
          class="search-input"
        />
        <select v-model="filterStatus" @change="handleFilterChange" class="status-filter">
          <option value="">All Items</option>
          <option value="not_added">Not Added</option>
          <option value="added">Added to Closet</option>
        </select>
      </div>
      <button class="add-btn" @click="openAddModal">
        + Add to Wishlist
      </button>
    </div>

    <!-- 心愿单项目网格 -->
    <div class="wishlist-grid">
      <div
        v-for="item in filteredItems"
        :key="item.wishlist_id"
        class="wishlist-card"
        :class="{ 'added': item.added_to_closet }"
      >
        <!-- 图片区域 -->
        <div class="wishlist-image" @click="viewItemDetail(item)">
          <img :src="getImageUrl(item.image_url)" :alt="item.name" />
          <div v-if="item.added_to_closet" class="added-badge">
            ✓ Added
          </div>
        </div>

        <!-- 信息区域 -->
        <div class="wishlist-info">
          <div class="info-header">
            <h3>{{ item.name }}</h3>
            <span class="price" v-if="item.price">${{ item.price.toFixed(2) }}</span>
          </div>

          <div class="brand" v-if="item.brand">{{ item.brand }}</div>

          <div class="tags">
            <span v-if="item.season" class="tag season">{{ item.season }}</span>
            <span v-if="item.color" class="tag color">{{ item.color }}</span>
            <span v-if="item.category" class="tag category">{{ item.category.category_name }}</span>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button
              v-if="!item.added_to_closet"
              class="btn-add"
              @click.stop="addToCloset(item)"
              :disabled="!item.category_id"
              :title="!item.category_id ? 'Please set category first' : ''"
            >
              Add to Closet
            </button>
            <button
              v-if="!item.added_to_closet"
              class="btn-find-similar"
              @click.stop="findSimilarItems(item)"
            >
              Find Similar
            </button>
            <button class="btn-delete" @click.stop="deleteItem(item)">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="wishlistItems.length === 0" class="empty-state">
      <div class="empty-icon">⭐</div>
      <h3>Your wishlist is empty</h3>
      <p>Start by adding clothes you want to add to your closet</p>
      <button class="add-btn-large" @click="openAddModal">
        + Add Your First Item
      </button>
    </div>

    <!-- 项目详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="detail-modal" @click.stop v-if="selectedItem">
        <button class="close-btn" @click="closeDetailModal">×</button>

        <div class="detail-header">
          <img :src="getImageUrl(selectedItem.image_url)" class="detail-image" />
          <div class="detail-info">
            <div class="brand">{{ selectedItem.brand || 'No brand' }}</div>
            <h2>{{ selectedItem.name }}</h2>
            <div class="detail-tags">
              <span class="tag season" v-if="selectedItem.season">{{ selectedItem.season }}</span>
              <span class="tag color" v-if="selectedItem.color">{{ selectedItem.color }}</span>
              <span class="tag occasion" v-if="selectedItem.occasion">{{ selectedItem.occasion }}</span>
              <span v-if="selectedItem.added_to_closet" class="added-badge">✓ Added to Closet</span>
            </div>
          </div>
        </div>

        <div class="detail-content">
          <div class="detail-item"><span class="label">Category:</span> {{ selectedItem.category?.category_name || 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Style:</span> {{ selectedItem.style || 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Material:</span> {{ selectedItem.material || 'Not specified' }}</div>
          <div class="detail-item"><span class="label">Price:</span> {{ selectedItem.price ? '$' + selectedItem.price.toFixed(2) : 'Not specified' }}</div>
          <div class="detail-item full-width">
            <span class="label">Notes:</span>
            <div class="notes-content">{{ selectedItem.notes || 'No notes' }}</div>
          </div>
        </div>

        <!-- 在模板的相似项目区域修改 -->
        <div v-if="similarItems.length > 0" class="similar-section">
          <h3>Similar Items in Your Closet</h3>
          <div class="similar-items">
            <div
              v-for="similar in similarItems"
              :key="similar.item_id"
              class="similar-item"
              @click="viewClosetItem(similar.item_id)"
            >
              <!-- 图片和基本信息 -->
              <div class="similar-header">
                <img
                  :src="getImageUrl(similar.image_url)"
                  :alt="similar.name"
                  class="similar-image"
                />
                <div class="similar-main-info">
                  <h4>{{ similar.name }}</h4>
                  <div class="similar-meta">
                    <span v-if="similar.brand">{{ similar.brand }}</span>
                    <span v-if="similar.category"> · {{ similar.category }}</span>
                    <span v-if="similar.price"> · ${{ similar.price.toFixed(2) }}</span>
                  </div>
                </div>
              </div>

              <!-- 相似度进度条 -->
              <div class="similarity-score">
                <div class="score-bar">
                  <div
                    class="score-fill"
                    :style="{ width: (similar.similarity_score * 100) + '%' }"
                    :class="{
                      'high': similar.similarity_score >= 0.7,
                      'medium': similar.similarity_score >= 0.4 && similar.similarity_score < 0.7,
                      'low': similar.similarity_score < 0.4
                    }"
                  ></div>
                </div>
                <span class="score-text">
                  {{ Math.round(similar.similarity_score * 100) }}% Match
                </span>
              </div>

              <!-- 匹配原因 -->
              <div class="match-reasons" v-if="similar.match_fields && similar.match_fields.length > 0">
                <span class="match-label">Matched on:</span>
                <div class="match-fields">
                  <span
                    v-for="field in similar.match_fields"
                    :key="field"
                    class="match-field"
                    :class="getMatchFieldClass(field)"
                  >
                    {{ formatMatchField(field) }}
                  </span>
                </div>
              </div>

              <!-- 详细匹配信息（可展开） -->
              <div class="match-details" v-if="similar.match_details">
                <div
                  class="details-toggle"
                  @click.stop="toggleMatchDetails(similar.item_id)"
                >
                  <span>Match Details</span>
                  <span class="toggle-icon">{{ showDetails[similar.item_id] ? '−' : '+' }}</span>
                </div>

                <div v-if="showDetails[similar.item_id]" class="details-content">
                  <div class="detail-row" v-if="similar.match_details.name_similarity">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{{ (similar.match_details.name_similarity * 100).toFixed(0) }}% similar</span>
                  </div>
                  <div class="detail-row" v-if="similar.match_details.brand_similarity">
                    <span class="detail-label">Brand:</span>
                    <span class="detail-value">{{ (similar.match_details.brand_similarity * 100).toFixed(0) }}% similar</span>
                  </div>
                  <div class="detail-row" v-if="similar.match_details.color_similarity">
                    <span class="detail-label">Color:</span>
                    <span class="detail-value">{{ (similar.match_details.color_similarity * 100).toFixed(0) }}% similar</span>
                  </div>
                  <div class="detail-row" v-if="similar.match_details.category_match">
                    <span class="detail-label">Category:</span>
                    <span class="detail-value">✓ Same category</span>
                  </div>
                  <div class="detail-row" v-if="similar.match_details.season_similarity">
                    <span class="detail-label">Season:</span>
                    <span class="detail-value">{{ (similar.match_details.season_similarity * 100).toFixed(0) }}% similar</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="detail-actions">
          <button v-if="!selectedItem.added_to_closet" class="btn-add" @click="addToCloset(selectedItem)">
            Add to Closet
          </button>
          <button class="btn-edit" @click="editItem(selectedItem)">
            Edit
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="add-modal" @click.stop>
        <h2>{{ editingItem ? 'Edit Wishlist Item' : 'Add to Wishlist' }}</h2>

        <form @submit.prevent="saveItem">
          <div class="form-grid">
            <div class="form-group">
              <label>Name *</label>
              <input v-model="formData.name" required />
            </div>
            <div class="form-group">
              <label>Category</label>
              <select v-model="formData.category_id">
                <option value="">Select category</option>
                <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
                  {{ cat.category_name }}
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
              <label>Price ($)</label>
              <input v-model="formData.price" type="number" step="0.01" min="0" />
            </div>
            <div class="form-group full-width">
              <label>Image URL</label>
              <input v-model="formData.image_url" placeholder="http://... or /static/..." />
            </div>
            <div class="form-group full-width">
              <label>Notes</label>
              <textarea v-model="formData.notes" rows="3" placeholder="Add any notes..."></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeAddModal">Cancel</button>
            <button type="submit">{{ editingItem ? 'Update' : 'Add to Wishlist' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()

// 状态定义
const wishlistItems = ref([])
const categories = ref([])
const selectedItem = ref(null)
const similarItems = ref([])
const stats = ref(null)
const loading = ref(false)
const showDetails = ref({})

// UI 状态
const showDetailModal = ref(false)
const showAddModal = ref(false)
const searchQuery = ref('')
const filterStatus = ref('')
const editingItem = ref(null)

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
  price: null,
  image_url: '',
  notes: ''
})

// 计算属性：过滤项目
const filteredItems = computed(() => {
  let items = wishlistItems.value

  // 按状态过滤
  if (filterStatus.value === 'not_added') {
    items = items.filter(item => !item.added_to_closet)
  } else if (filterStatus.value === 'added') {
    items = items.filter(item => item.added_to_closet)
  }

  // 按搜索词过滤
  if (searchQuery.value.trim()) {
    const keyword = searchQuery.value.trim().toLowerCase()
    items = items.filter(item =>
      item.name?.toLowerCase().includes(keyword) ||
      item.brand?.toLowerCase().includes(keyword) ||
      item.color?.toLowerCase().includes(keyword) ||
      item.notes?.toLowerCase().includes(keyword)
    )
  }

  return items
})

// 方法
const fetchWishlistItems = async () => {
  try {
    loading.value = true
    const res = await request.get('/api/wishlist/items')
    wishlistItems.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch wishlist items:', error)
    alert('Failed to load wishlist items')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await request.get('/api/closet/categories')
    categories.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchStats = async () => {
  try {
    const res = await request.get('/api/wishlist/stats')
    stats.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const addToCloset = async (item) => {
  if (!item.category_id) {
    alert('Please set a category before adding to closet')
    return
  }

  if (!confirm('Add this item to your closet?')) return

  try {
    const res = await request.post(`/api/wishlist/items/${item.wishlist_id}/add-to-closet`)
    alert('Item added to closet successfully!')

    // 刷新数据
    await fetchWishlistItems()
    await fetchStats()
  } catch (error) {
    console.error('Failed to add to closet:', error)
    alert(error.response?.data?.detail || 'Failed to add to closet')
  }
}

const findSimilarItems = async (item) => {
  try {
    const res = await request.get(`/api/wishlist/items/${item.wishlist_id}/similar-items`, {
      params: {
        threshold: 0.01,  // 相似度阈值，可以调整
        limit: 10        // 返回数量限制
      }
    })
    similarItems.value = res.data || res

    if (similarItems.value.length > 0) {
      selectedItem.value = item
      showDetailModal.value = true
      showDetails.value = {}
    } else {
      alert('No similar items found in your closet')
    }
  } catch (error) {
    console.error('Failed to find similar items:', error)
    alert('Failed to find similar items: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteItem = async (item) => {
  if (!confirm('Are you sure you want to delete this item?')) return

  try {
    await request.delete(`/api/wishlist/items/${item.wishlist_id}`)
    alert('Item deleted successfully')

    // 刷新数据
    await fetchWishlistItems()
    await fetchStats()
  } catch (error) {
    console.error('Failed to delete item:', error)
    alert('Failed to delete item')
  }
}

const viewItemDetail = (item) => {
  selectedItem.value = item
  similarItems.value = []
  showDetailModal.value = true
}

const viewClosetItem = (itemId) => {
  closeDetailModal()
  router.push(`/closet/item/${itemId}`)
}

const openAddModal = () => {
  editingItem.value = null
  resetForm()
  showAddModal.value = true
}

const editItem = (item) => {
  editingItem.value = item
  Object.assign(formData, {
    name: item.name,
    category_id: item.category_id || '',
    brand: item.brand || '',
    color: item.color || '',
    season: item.season || '',
    occasion: item.occasion || '',
    style: item.style || '',
    material: item.material || '',
    price: item.price || null,
    image_url: item.image_url || '',
    notes: item.notes || ''
  })
  showDetailModal.value = false
  showAddModal.value = true
}

const saveItem = async () => {
  try {
    const payload = { ...formData }

    // 处理空值
    if (payload.occasion?.trim() === '') payload.occasion = null
    if (payload.color?.trim() === '') payload.color = null
    if (payload.season?.trim() === '') payload.season = null
    if (payload.style?.trim() === '') payload.style = null
    if (payload.material?.trim() === '') payload.material = null
    if (payload.notes?.trim() === '') payload.notes = null

    // 处理价格
    if (payload.price) {
      payload.price = parseFloat(payload.price)
    } else {
      payload.price = null
    }

    if (editingItem.value) {
      await request.put(`/api/wishlist/items/${editingItem.value.wishlist_id}`, payload)
      alert('Item updated successfully!')
    } else {
      await request.post('/api/wishlist/items', payload)
      alert('Item added to wishlist successfully!')
    }

    closeAddModal()

    // 刷新数据
    await fetchWishlistItems()
    await fetchStats()
  } catch (error) {
    console.error('Failed to save item:', error)
    alert(error.response?.data?.detail || 'Failed to save item')
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedItem.value = null
  similarItems.value = []
}

const closeAddModal = () => {
  showAddModal.value = false
  editingItem.value = null
  resetForm()
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === 'price') {
      formData[key] = null
    } else {
      formData[key] = ''
    }
  })
}

const getImageUrl = (url) => {
  if (!url) return '/placeholder.png'
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}

const handleSearch = () => {
  // 搜索逻辑
}

const handleFilterChange = () => {
  // 筛选逻辑
}

// 初始化
onMounted(() => {
  fetchWishlistItems()
  fetchCategories()
  fetchStats()
})

const formatMatchField = (field) => {
  const fieldMap = {
    'name': 'Name',
    'brand': 'Brand',
    'color': 'Color',
    'category': 'Category',
    'season': 'Season',
    'occasion': 'Occasion',
    'style': 'Style'
  }
  return fieldMap[field] || field.charAt(0).toUpperCase() + field.slice(1)
}

const getMatchFieldClass = (field) => {
  return `match-${field}`
}

const toggleMatchDetails = (itemId) => {
  showDetails.value[itemId] = !showDetails.value[itemId]
}

const getMatchSuggestion = (similarityScore) => {
  if (similarityScore >= 0.8) {
    return 'Very similar item, consider if you need both'
  } else if (similarityScore >= 0.6) {
    return 'Quite similar, might be alternative'
  } else if (similarityScore >= 0.4) {
    return 'Some similarities, check details'
  } else {
    return 'Slightly similar'
  }
}

const compareItems = (wishlistItem, closetItem) => {
  // 可以跳转到比较页面或打开比较模态框
  console.log('Comparing:', wishlistItem, closetItem)
  // 这里可以扩展为打开一个比较模态框
  openComparisonModal(wishlistItem, closetItem)
}

// 新增：打开比较模态框
const openComparisonModal = (item1, item2) => {
  // 实现比较模态框的逻辑
  alert(`Compare: ${item1.name} vs ${item2.name}`)
}
</script>

<style scoped>
.wishlist {
  padding: 20px;
  font-family: 'Inter', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

/* 头部样式 */
.header {
  margin-bottom: 30px;
}

.header h1 {
  margin: 0 0 5px 0;
  color: #1e293b;
  font-size: 32px;
}

.subtitle {
  color: #64748b;
  margin-bottom: 20px;
  font-size: 14px;
}

/* 统计信息 */
.stats-bar {
  display: flex;
  gap: 30px;
  margin-top: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #6366f1;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 5px;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
  flex: 1;
  max-width: 500px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
}

.status-filter {
  padding: 10px 15px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}

.add-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
}

.add-btn:hover {
  background: #4f46e5;
}

/* 心愿单网格 */
.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.wishlist-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: 0.2s;
}

.wishlist-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.wishlist-card.added {
  opacity: 0.8;
  background: #f8fafc;
}

/* 图片区域 */
.wishlist-image {
  position: relative;
  height: 200px;
  background: #f1f5f9;
  cursor: pointer;
}

.wishlist-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.added-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #10b981;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

/* 信息区域 */
.wishlist-info {
  padding: 15px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.info-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1e293b;
  flex: 1;
}

.price {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.brand {
  color: #64748b;
  font-size: 12px;
  margin-bottom: 10px;
}

/* 标签样式 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
}

.tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
}

.tag.season {
  background: #dbeafe;
  color: #1e40af;
}

.tag.color {
  background: #fef3c7;
  color: #92400e;
}

.tag.category {
  background: #dcfce7;
  color: #065f46;
}

.tag.occasion {
  background: #f3e8ff;
  color: #7c3aed;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons button {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  flex: 1;
  min-width: 80px;
}

.btn-add {
  background: #6366f1;
  color: white;
}

.btn-add:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.btn-find-similar {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #1e293b;
  margin-bottom: 10px;
}

.empty-state p {
  margin-bottom: 20px;
}

.add-btn-large {
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  padding: 20px;
}

.detail-modal, .add-modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  border: none;
  background: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
}

/* 详情头部 */
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
  font-size: 12px;
  margin-bottom: 5px;
}

.detail-info h2 {
  margin: 0 0 10px 0;
  color: #1e293b;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

/* 详情内容 */
.detail-content {
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.label {
  font-weight: 600;
  color: #64748b;
  font-size: 12px;
}

.notes-content {
  white-space: pre-line;
  background: #f8fafc;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
}

/* 相似项目区域 */
.similar-header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.similar-image {
  width: 60px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  background: #f1f5f9;
}

.similar-main-info {
  flex: 1;
}

.similar-main-info h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
}

.similar-meta {
  font-size: 12px;
  color: #64748b;
}

.similar-meta span {
  margin-right: 8px;
}

.similar-section {
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
}

.similar-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #1e293b;
}

.similar-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.similar-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
  transition: 0.2s;
}

.similar-item:hover {
  background: #f1f5f9;
  transform: translateX(5px);
}

.similar-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.similar-match {
  font-size: 11px;
  color: #6366f1;
  margin-bottom: 5px;
}

.similarity-score {
  margin-bottom: 10px;
}

.score-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  margin-bottom: 5px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.score-fill.high {
  background: #10b981; /* 绿色 */
}

.score-fill.medium {
  background: #f59e0b; /* 黄色 */
}

.score-fill.low {
  background: #ef4444; /* 红色 */
}

.score-text {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.match-reasons {
  margin-bottom: 10px;
}

.match-label {
  font-size: 11px;
  color: #64748b;
  margin-right: 8px;
  font-weight: 500;
}

.match-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 5px;
}

.match-field {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.match-name {
  background: #dbeafe;
  color: #1e40af;
}

.match-brand {
  background: #fef3c7;
  color: #92400e;
}

.match-color {
  background: #fee2e2;
  color: #991b1b;
}

.match-category {
  background: #dcfce7;
  color: #065f46;
}

.match-season {
  background: #f3e8ff;
  color: #7c3aed;
}

.match-occasion {
  background: #fce7f3;
  color: #be185d;
}

.match-style {
  background: #e0f2fe;
  color: #0369a1;
}

/* 详细匹配信息 */
.match-details {
  border-top: 1px solid #e2e8f0;
  padding-top: 10px;
  margin-top: 10px;
}

.details-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-size: 12px;
  color: #6366f1;
  font-weight: 500;
  padding: 5px 0;
}

.details-toggle:hover {
  color: #4f46e5;
}

.toggle-icon {
  font-weight: bold;
  font-size: 14px;
}

.details-content {
  margin-top: 10px;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 11px;
  color: #1e293b;
  font-weight: 600;
}

/* 详情操作按钮 */
.detail-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.detail-actions button {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.detail-actions .btn-add {
  background: #6366f1;
  color: white;
}

.detail-actions .btn-edit {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

/* 相似项目操作按钮 */
.similar-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.similar-actions button {
  flex: 1;
  padding: 6px 12px;
  font-size: 11px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.similar-actions button:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.similar-actions button:first-child {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

.similar-actions button:first-child:hover {
  background: #4f46e5;
}

/* 空状态提示 */
.no-similar-items {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 14px;
}

.no-similar-items .icon {
  font-size: 32px;
  margin-bottom: 10px;
}

/* 加载状态 */
.similar-loading {
  text-align: center;
  padding: 20px;
  color: #64748b;
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

.form-group.full-width {
  grid-column: 1 / -1;
}

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

.form-group textarea {
  resize: vertical;
}

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

/* 加载状态 */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .wishlist-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }

  .stats-bar {
    flex-direction: column;
    gap: 15px;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar {
    max-width: 100%;
  }

  .detail-header {
    flex-direction: column;
  }

  .detail-image {
    width: 100%;
    height: 200px;
  }

  .detail-content {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .similar-header {
    flex-direction: column;
  }

  .similar-image {
    width: 100%;
    height: 120px;
  }

  .similar-actions {
    flex-direction: column;
  }
}
</style>