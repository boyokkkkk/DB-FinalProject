<template>
  <div class="manager-container">
    
    <transition name="fade-slide" mode="out-in">
      
      <OutfitStudio 
        v-if="isEditing" 
        :initial-data="currentEditData"
        @back="closeStudio"
        @save="handleSaveLook"
      />
      
      <div v-else class="gallery-view">
        <div class="gallery-header">
          <div class="header-bg-decor"></div>
          <div class="header-main">
            <div class="title-section">
              <h1>Digital Wardrobe</h1>
              <p>Create, organize, and visualize your daily style.</p>
            </div>
            
            <div class="search-toolbar">
               <el-input 
                  v-model="searchQuery" 
                  placeholder="Search outfits..." 
                  prefix-icon="Search"
                  size="large"
                  class="search-input"
                  clearable
               />
               <div class="actions">
                 <el-button type="primary" size="large" icon="Plus" round color="#6366f1" class="create-btn" @click="openStudio(null)">
                   New Look
                 </el-button>
               </div>
            </div>

            <div class="filter-tabs">
              <span 
                v-for="tab in filters" 
                :key="tab" 
                class="tab-item" 
                :class="{ active: activeFilter === tab }" 
                @click="activeFilter = tab"
              >
                {{ tab }}
              </span>
            </div>
          </div>
        </div>

        <div class="gallery-scroll-area custom-scrollbar">
          <div class="gallery-grid">
            
            <div class="look-card create-card" @click="openStudio(null)">
              <div class="dashed-content">
                <div class="icon-circle"><el-icon :size="24"><Plus /></el-icon></div>
                <span>Create New</span>
              </div>
            </div>

            <div 
              v-for="look in filteredLooks" 
              :key="look.outfit_id" 
              class="look-card"
              @click="editOutfit(look.outfit_id)" 
            >
              <div class="card-cover" :style="{ background: '#f8fafc' }">
                 <div class="preview-emoji">
                    <span v-if="look.season === 'Winter'">❄️</span>
                    <span v-else-if="look.season === 'Summer'">☀️</span>
                    <span v-else-if="look.style === 'Formal'">👔</span>
                    <span v-else>✨</span>
                 </div>
                 
                 <div class="hover-overlay">
                   <div class="overlay-text">Click to Edit</div>
                   <el-button circle icon="Delete" type="danger" plain @click.stop="deleteLook(look.outfit_id)" />
                 </div>
              </div>
              
              <div class="card-info">
                <div class="info-top">
                  <span class="look-title">{{ look.name }}</span>
                </div>
                
                <div class="tags-row">
                  <el-tag v-if="look.season" size="small" effect="plain" type="warning" round>{{ look.season }}</el-tag>
                  <el-tag v-if="look.style" size="small" effect="plain" type="" round>{{ look.style }}</el-tag>
                </div>
                
                <div class="info-footer">
                  <span class="desc-text">{{ look.item_count }} items</span>
                  <span class="date-text">{{ formatDate(look.create_time) }}</span>
                </div>
              </div>
            </div>

          </div>
          
          <div v-if="filteredLooks.length === 0" class="empty-state">
             <el-empty description="No outfits found" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Search, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import OutfitStudio from './OutfitBoard.vue'
import request from '../utils/request'

const isEditing = ref(false)
const searchQuery = ref('')
const activeFilter = ref('All')
const currentEditData = ref(null)

const getImageUrl = (url) => {
    if (!url) return ''
    if (url.startsWith('http')) return url
    return `http://127.0.0.1:8000${url}`
}

// [修复2] 这里定义了 Tab 的来源。去掉 Favorites，因为它需要后端支持。
const filters = ['All', 'Summer', 'Winter', 'Casual', 'Formal']

const lookList = ref([])

// 搜索与过滤逻辑
const filteredLooks = computed(() => {
  let result = lookList.value
  
  // 1. 根据 Tab 过滤 (匹配 Season 或 Style)
  if (activeFilter.value !== 'All') {
     result = result.filter(l => 
        l.season === activeFilter.value || l.style === activeFilter.value
     )
  }

  // 2. 根据搜索框过滤
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(l => l.name.toLowerCase().includes(q))
  }
  
  return result
})

// 获取列表
const fetchOutfits = async () => {
  try {
    const res = await request.get('/api/outfits/')
    lookList.value = res 
  } catch (error) {
    console.error('获取搭配列表失败', error)
  }
}

// 打开新建模式
const openStudio = (data) => {
  currentEditData.value = data
  isEditing.value = true
}

// [修复3] 核心逻辑：点击卡片，获取详情并转换为前端画布格式
const editOutfit = async (outfitId) => {
  try {
    // 1. 请求后端详情接口
    const res = await request.get(`/api/outfits/${outfitId}`)
    
    // 2. 将后端的数据结构 (OutfitRef) 转换回前端画布需要的结构 (Elements)
    const canvasElements = res.items.map(item => ({
      id: Date.now() + Math.random(), // 生成一个临时前端ID
      itemId: item.item_id,           // 记录真实数据库ID
      type: 'image',                  // 类型固定为 image
      // 记得拼上后端地址
      src: getImageUrl(item.image_url),
      x: item.position_x,
      y: item.position_y,
      w: item.scale_x, // 我们之前约定 scale_x 存宽度
      h: item.scale_y, // scale_y 存高度
      rotate: item.rotation,
      zIndex: item.z_index,
      opacity: 1
    }))

    // 3. 构造传递给 OutfitBoard 的 initialData
    const editData = {
      outfit_id: res.outfit_id, // 记录 ID，以便后续如果是更新逻辑可以用（目前只实现了新建）
      title: res.name,
      note: res.description,
      season: res.season,
      style: res.style,
      bg: '#ffffff', // 后端还没存背景色，暂时默认白
      elements: canvasElements // 放入转换好的元素
    }

    openStudio(editData)

  } catch (error) {
    console.error('无法加载搭配详情', error)
    ElMessage.error('加载详情失败')
  }
}

const closeStudio = () => {
  isEditing.value = false
  currentEditData.value = null
  fetchOutfits()
}

// 保存逻辑
const handleSaveLook = async (data) => {
  // data 是从 OutfitBoard 传出来的
  const outfitItems = data.elements
    .filter(el => el.type === 'image' && el.itemId)
    .map(el => ({
      item_id: el.itemId,
      position_x: el.x,
      position_y: el.y,
      rotation: el.rotate,
      scale_x: el.w, 
      scale_y: el.h,
      z_index: el.zIndex
    }))

  if (outfitItems.length === 0) {
    ElMessage.warning('画布为空，无法保存')
    return
  }

  const userTags = data.tags || []
  const knownSeasons = ['Spring', 'Summer', 'Autumn', 'Winter']
  const knownStyles = ['Casual', 'Formal', 'Work', 'Sporty', 'Chic', 'Party']

  let detectedSeason = knownSeasons.find(s => userTags.includes(s)) || 'All'
  let detectedStyle = knownStyles.find(s => userTags.includes(s)) || 'Casual'

  const payload = {
    name: data.title,
    description: data.note,
    season: detectedSeason, // 使用解析出来的季节
    style: detectedStyle,   // 使用解析出来的风格
    image_url: '',
    items: outfitItems
  }

  try {
    // 注意：目前后端只实现了 POST (新建)。
    // 如果想要实现“修改”，后端需要加 PUT 接口，这里先都当做新建处理
    await request.post('/api/outfits/', payload)
    ElMessage.success('搭配已保存！')
    
    isEditing.value = false
    fetchOutfits() 
  } catch (error) {
    console.error(error)
  }
}

const deleteLook = (id) => {
  ElMessageBox.confirm('确定删除?', '提示', { type: 'warning' })
  .then(async () => {
    try {
      await request.delete(`/api/outfits/${id}`)
      ElMessage.success('已删除')
      fetchOutfits()
    } catch (e) {}
  })
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchOutfits()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

.manager-container { width: 100%; height: 100%; background-color: #f1f5f9; display: flex; flex-direction: column; overflow: hidden; font-family: 'Inter', sans-serif; }
.gallery-view { flex: 1; display: flex; flex-direction: column; height: 100%; }
.gallery-header { background: #fff; border-bottom: 1px solid #e2e8f0; flex-shrink: 0; }
.header-bg-decor { height: 6px; background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); }
.header-main { padding: 32px 40px 0; max-width: 1200px; margin: 0 auto; width: 100%; box-sizing: border-box; }
.title-section h1 { font-family: 'Playfair Display', serif; font-size: 32px; color: #1e293b; margin: 0 0 8px 0; }
.title-section p { color: #64748b; margin: 0 0 24px 0; font-size: 15px; }
.search-toolbar { display: flex; gap: 16px; margin-bottom: 32px; }
.search-input { flex: 1; max-width: 500px; }
.filter-tabs { display: flex; gap: 32px; border-bottom: 1px solid transparent; }
.tab-item { padding-bottom: 16px; font-size: 14px; color: #64748b; cursor: pointer; position: relative; font-weight: 500; transition: color 0.2s; }
.tab-item:hover { color: #334155; }
.tab-item.active { color: #6366f1; font-weight: 600; }
.tab-item.active::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 100%; height: 3px; background: #6366f1; border-top-left-radius: 3px; border-top-right-radius: 3px; }

.gallery-scroll-area { flex: 1; overflow-y: auto; padding: 32px 40px; }
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 32px; max-width: 1200px; margin: 0 auto; padding-bottom: 60px; }

.look-card { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); cursor: pointer; transition: 0.3s; border: 1px solid transparent; }
.look-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #e2e8f0; }

.create-card { background: rgba(255,255,255,0.5); border: 2px dashed #cbd5e1; box-shadow: none; min-height: 280px; display: flex; }
.create-card:hover { border-color: #6366f1; background: #eef2ff; transform: translateY(-4px); }
.dashed-content { width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; color: #64748b; font-weight: 600; }
.icon-circle { width: 48px; height: 48px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #fff; transition: 0.3s; }
.create-card:hover .icon-circle { background: #6366f1; transform: scale(1.1); }

.card-cover { height: 180px; display: flex; align-items: center; justify-content: center; position: relative; font-size: 48px; }
.preview-emoji { opacity: 0.8; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }
.hover-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(2px); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; opacity: 0; transition: 0.3s; }
.look-card:hover .hover-overlay { opacity: 1; }
.overlay-text { color: white; font-weight: 600; font-size: 14px; margin-bottom: 8px; }

.card-info { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.info-top { display: flex; justify-content: space-between; align-items: center; }
.look-title { font-weight: 700; color: #1e293b; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 标签样式 */
.tags-row { display: flex; gap: 6px; flex-wrap: wrap; }

.info-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; padding-top: 12px; border-top: 1px solid #f1f5f9; }
.desc-text { font-size: 12px; color: #64748b; font-weight: 500; }
.date-text { font-size: 11px; color: #94a3b8; }

.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; border: 2px solid #f1f5f9; }
.empty-state { padding: 60px 0; }
</style>