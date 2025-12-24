<template>
  <div class="studio-container" @click.self="deselectAll" tabindex="0" @keydown="handleKeyDown">
    
    <div class="studio-sidebar">
      <div class="sidebar-header">
        <div class="header-title">Studio Assets</div>
        <div class="header-subtitle">Create your unique look</div>
      </div>
      
      <div class="nav-capsules">
        <div 
          v-for="tab in tabs" :key="tab.key"
          class="capsule-btn" :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
        </div>
      </div>

      <div class="assets-scroll-area custom-scrollbar">
        <div v-if="activeTab === 'wardrobe'" class="assets-wrapper">
          <div class="category-tags">
             <span class="cat-tag" :class="{ active: activeCategory === 'All' }" @click="activeCategory = 'All'">All</span>
             <span v-for="cat in dynamicWardrobeCats" :key="cat" class="cat-tag" :class="{ active: activeCategory === cat }" @click="activeCategory = cat">{{ cat }}</span>
          </div>
          
          <div class="grid-2-col">
            <div v-for="item in filteredItems" :key="item.item_id" class="asset-item" draggable="true" @dragstart="onDragStart($event, item, 'image')">
              <div class="img-holder">
                <el-image :src="getImageUrl(item.image_url)" fit="contain" loading="lazy" class="draggable-img" crossorigin="anonymous" />
              </div>
            </div>
            <div v-if="filteredItems.length === 0" class="no-items-tip">No items in this category</div>
          </div>
        </div>

        <div v-if="activeTab === 'background'" class="assets-wrapper">
          <div class="section-label">Solid Colors</div>
          <div class="color-palette">
            <div v-for="c in solidColors" :key="c" class="color-dot" :style="{background: c}" @click="setBackground('color', c)"></div>
          </div>
          <div class="section-label mt-4">Textures</div>
          <div class="grid-2-col">
            <div v-for="tex in textures" :key="tex.name" class="asset-item texture-item" :style="{backgroundImage: `url(${tex.url})`}" @click="setBackground('image', tex.url)">
               <span>{{ tex.name }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'text'" class="assets-wrapper">
           <div class="list-stack">
             <div v-for="txt in textPresets" :key="txt.label" class="text-preset-card" :style="{fontFamily: txt.font}" draggable="true" @dragstart="onDragStart($event, txt, 'text')">{{ txt.label }}</div>
           </div>
        </div>

        <div v-if="activeTab === 'sticker'" class="assets-wrapper">
           <div class="grid-3-col">
             <div v-for="s in stickers" :key="s.id" class="sticker-item" draggable="true" @dragstart="onDragStart($event, s, 'sticker')">
                <img :src="s.url" class="draggable-img" crossorigin="anonymous" />
             </div>
           </div>
        </div>
      </div>
    </div>

    <div class="studio-workspace">
      <div class="toolbar-island">
        <div class="left-group">
          <el-button circle plain icon="ArrowLeft" class="icon-btn" @click="$emit('back')" />
          <div class="divider-v"></div>
          <div class="project-info">
            <span class="p-name">{{ saveForm.title || 'Untitled Look' }}</span>
            <span class="p-status">Editing</span>
          </div>
        </div>
        
        <div class="tools-center">
           <el-button-group class="zoom-group">
             <el-button link icon="Minus" @click="zoom -= 10" />
             <span class="zoom-val">{{ zoom }}%</span>
             <el-button link icon="Plus" @click="zoom += 10" />
           </el-button-group>
           <el-divider direction="vertical" />
           <el-tooltip content="Reset View"><el-button link icon="FullScreen" @click="resetView" /></el-tooltip>
        </div>

        <div class="actions-right">
           <el-button text bg circle icon="Delete" class="danger-icon" @click="clearCanvas" />
           <el-button type="primary" round color="#6366f1" class="save-btn" :loading="isSaving" @click="openSaveDialog">
             Save Look
           </el-button>
        </div>
      </div>

      <div class="canvas-viewport" @mousedown.self="deselectAll">
        <div class="canvas-artboard" 
             id="artboard"
             :style="artboardStyle"
             @drop="onDrop"
             @dragover.prevent
             @mousedown.self="deselectAll">
             
             <div v-if="elements.length === 0 && !bgImage" class="empty-guide">
                <el-icon :size="48" color="#dbeafe"><Picture /></el-icon>
                <p>Drag items here to start designing</p>
             </div>

             <div v-for="(el, index) in elements" :key="el.id"
                  class="layer-box"
                  :class="{ selected: selectedIndex === index }"
                  :style="getLayerStyle(el)"
                  @mousedown.stop="startDrag($event, index)">
                
                <div class="layer-content" :style="getContentStyle(el)">
                   <img v-if="el.type === 'image' || el.type === 'sticker'" 
                        :src="el.src" draggable="false" crossorigin="anonymous" />
                   
                   <div v-if="el.type === 'text'" 
                        class="text-element"
                        :contenteditable="selectedIndex === index"
                        @blur="updateText($event, index)"
                        @input="handleTextInput"
                        v-html="el.text">
                   </div>
                </div>

                <div v-if="selectedIndex === index" class="transform-controls">
                   <div class="control-knob rotate" @mousedown.stop="startRotate($event)">
                      <el-icon><RefreshRight /></el-icon>
                   </div>
                   <div class="control-knob resize-br" @mousedown.stop="startResize($event)"></div>
                   <div class="border-outline"></div>
                </div>
             </div>
        </div>
      </div>

      <transition name="slide-up">
        <div v-if="selectedIndex !== -1" class="property-floater">
          <div class="prop-section">
            <span class="label">Layer</span>
            <el-button-group>
               <el-button size="small" icon="ArrowUp" @click="moveLayer(1)" />
               <el-button size="small" icon="ArrowDown" @click="moveLayer(-1)" />
            </el-button-group>
            <el-button size="small" type="danger" plain icon="Delete" @click="deleteLayer" class="ml-2" />
          </div>
          <div class="divider"></div>
          <div v-if="currentEl.type !== 'text'" class="prop-section">
             <span class="label">Opacity</span>
             <el-slider v-model="currentEl.opacity" :min="0.2" :max="1" :step="0.1" size="small" style="width: 80px" />
          </div>
          <div v-if="currentEl.type === 'text'" class="prop-section">
             <el-color-picker v-model="currentEl.color" size="small" show-alpha />
             <el-select v-model="currentEl.fontFamily" size="small" style="width: 110px" class="ml-2 mini-select">
                <el-option label="Serif" value="'Playfair Display', serif" />
                <el-option label="Sans" value="'Inter', sans-serif" />
                <el-option label="Handwriting" value="cursive" />
             </el-select>
             <el-input-number v-model="currentEl.fontSize" size="small" :min="12" :max="200" style="width: 90px" class="ml-2" />
          </div>
        </div>
      </transition>
    </div>

    <el-dialog
      v-model="saveDialogVisible"
      title="Save Your Outfit"
      width="400px"
      align-center
      class="custom-dialog"
      :close-on-click-modal="!isSaving"
      :show-close="!isSaving"
    >
      <el-form :model="saveForm" label-position="top">
        <el-form-item label="Outfit Name">
          <el-input v-model="saveForm.title" placeholder="e.g. Summer Date Night" />
        </el-form-item>
        
        <div class="grid-2-col-form">
          <el-form-item label="Season">
            <el-select v-model="saveForm.season" placeholder="Select Season">
              <el-option label="Spring" value="Spring" />
              <el-option label="Summer" value="Summer" />
              <el-option label="Autumn" value="Autumn" />
              <el-option label="Winter" value="Winter" />
              <el-option label="All Year" value="All Year" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Style">
            <el-select v-model="saveForm.style" placeholder="Select Style" allow-create filterable>
              <el-option label="Casual" value="Casual" />
              <el-option label="Formal" value="Formal" />
              <el-option label="Work" value="Work" />
              <el-option label="Party" value="Party" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="Notes">
          <el-input v-model="saveForm.note" type="textarea" :rows="3" placeholder="Add styling tips..." />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="saveDialogVisible = false" :disabled="isSaving">Cancel</el-button>
          <el-button type="primary" color="#6366f1" :loading="isSaving" @click="confirmSave">
            {{ isSaving ? 'Saving...' : 'Save Outfit' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Goods, Picture, EditPen, MagicStick, Minus, Plus, FullScreen, Delete, RefreshRight, ArrowUp, ArrowDown, ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'
import html2canvas from 'html2canvas' // 确保已安装

const getImageUrl = (url) => {
  if (!url) return ''
  // 如果已经是网络图片 (http开头) 或 base64 (data:image开头)，直接返回
  if (url.startsWith('http') || url.startsWith('data:image')) return url
  
  // 拼接后端地址，注意处理斜杠
  const baseUrl = 'http://127.0.0.1:8000'
  return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`
}

const props = defineProps({
  initialData: { type: Object, default: null }
})
const emit = defineEmits(['back', 'save'])

const activeTab = ref('wardrobe')
const activeCategory = ref('All')
const zoom = ref(100)
const selectedIndex = ref(-1)
const isSaving = ref(false)

const bgColor = ref('#ffffff')
const bgImage = ref('')
const elements = ref([]) 

const saveDialogVisible = ref(false)
const saveForm = reactive({
  title: '',
  season: 'All Year',
  style: 'Casual',
  note: ''
})

let draggedItem = null 
let isInteracting = false
let startX = 0, startY = 0
let initialParams = {} 

// Assets
const tabs = [
  { key: 'wardrobe', label: 'Items', icon: 'Goods' },
  { key: 'background', label: 'Canvas', icon: 'Picture' },
  { key: 'text', label: 'Typography', icon: 'EditPen' },
  { key: 'sticker', label: 'Decor', icon: 'MagicStick' }
]

const realWardrobe = ref([])

const dynamicWardrobeCats = computed(() => {
  if (!realWardrobe.value || realWardrobe.value.length === 0) return []
  const cats = new Set(realWardrobe.value.map(item => item.category))
  return Array.from(cats).sort()
})

const filteredItems = computed(() => {
  if (activeCategory.value === 'All') return realWardrobe.value
  return realWardrobe.value.filter(i => i.category === activeCategory.value)
})

const solidColors = ['#ffffff', '#f8fafc', '#fef2f2', '#fffbeb', '#f0fdf4', '#eff6ff', '#f5f3ff']
const textures = [
  { name: 'Paper', url: 'http://127.0.0.1:8000/static/textures/cream-paper.png' },
  { name: 'Grid', url: 'http://127.0.0.1:8000/static/textures/graphy.png' }
]
const textPresets = [
    { label: 'Title Serif', font: "'Playfair Display', serif" },
    { label: 'Body Sans', font: "'Inter', sans-serif" },
    { label: 'Signature', font: "cursive" }
]
const stickers = [
    { id: 's1', url: 'https://cdn-icons-png.flaticon.com/512/1828/1828884.png' }, 
    { id: 's2', url: 'https://cdn-icons-png.flaticon.com/512/2909/2909241.png' } 
]

const currentEl = computed(() => selectedIndex.value !== -1 ? elements.value[selectedIndex.value] : {})

const artboardStyle = computed(() => ({
    width: '600px',
    height: '600px',
    backgroundColor: bgColor.value,
    backgroundImage: bgImage.value ? `url(${bgImage.value})` : 'none',
    transform: `scale(${zoom.value / 100})`,
    transformOrigin: 'center center',
    transition: 'transform 0.1s linear'
}))

// Canvas Interaction Logic
const getLayerStyle = (el) => ({
    top: `${el.y}px`,
    left: `${el.x}px`,
    width: `${el.w}px`,
    height: el.type === 'text' ? 'auto' : `${el.h}px`,
    zIndex: el.zIndex,
    transform: `rotate(${el.rotate}deg)`,
    position: 'absolute',
    transformOrigin: 'center center',
})
const getContentStyle = (el) => ({
    width: '100%',
    height: '100%',
    opacity: el.opacity,
    color: el.color,
    fontFamily: el.fontFamily,
    fontSize: `${el.fontSize}px`
})
const onDragStart = (e, item, type) => {
    let ratio = 1
    if (type === 'image' || type === 'sticker') {
        const imgEl = e.target.querySelector('img') || (e.target.tagName === 'IMG' ? e.target : null)
        if (imgEl && imgEl.naturalWidth && imgEl.naturalHeight) {
            ratio = imgEl.naturalHeight / imgEl.naturalWidth
        }
    }
    draggedItem = { item, type, ratio }
}
const onDrop = (e) => {
    e.preventDefault()
    if (!draggedItem) return
    const rect = document.getElementById('artboard').getBoundingClientRect()
    const scale = zoom.value / 100
    const mouseX = (e.clientX - rect.left) / scale
    const mouseY = (e.clientY - rect.top) / scale
    const newId = Date.now()
    const baseZ = elements.value.length + 1
    
    if (draggedItem.type === 'image' || draggedItem.type === 'sticker') {
        const baseWidth = 150
        const calculatedHeight = baseWidth * draggedItem.ratio
        elements.value.push({
            id: newId, itemId: draggedItem.item.item_id, type: 'image', src: getImageUrl(draggedItem.item.image_url),
            x: mouseX - (baseWidth / 2), y: mouseY - (calculatedHeight / 2), w: baseWidth, h: calculatedHeight, 
            rotate: 0, zIndex: baseZ, opacity: 1
        })
    } else if (draggedItem.type === 'text') {
        elements.value.push({
            id: newId, type: 'text', text: 'Double click to edit',
            x: mouseX - 100, y: mouseY - 20, w: 200, h: 50, rotate: 0, zIndex: baseZ, opacity: 1,
            color: '#333', fontSize: 24, fontFamily: draggedItem.item.font
        })
    }
    selectedIndex.value = elements.value.length - 1
    draggedItem = null
}
const setBackground = (type, val) => { if (type === 'color') { bgColor.value = val; bgImage.value = '' } else { bgImage.value = val } }
const startDrag = (e, index) => { if (e.button !== 0 || e.target.classList.contains('control-knob')) return; selectedIndex.value = index; isInteracting = true; startX = e.clientX; startY = e.clientY; initialParams = { ...elements.value[index] }; document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', stopInteraction) }
const onMove = (e) => { if (!isInteracting) return; const scale = zoom.value / 100; elements.value[selectedIndex.value].x = initialParams.x + (e.clientX - startX) / scale; elements.value[selectedIndex.value].y = initialParams.y + (e.clientY - startY) / scale }
const startRotate = (e) => { e.stopPropagation(); const el = document.getElementById('artboard').getBoundingClientRect(); const item = elements.value[selectedIndex.value]; const centerX = el.left + (item.x + item.w/2) * (zoom.value/100); const centerY = el.top + (item.y + item.h/2) * (zoom.value/100); initialParams = { startRotate: item.rotate, startAngle: Math.atan2(e.clientY - centerY, e.clientX - centerX) }; isInteracting = true; const onRotateMove = (ev) => { const deg = Math.atan2(ev.clientY - centerY, ev.clientX - centerX) - initialParams.startAngle; elements.value[selectedIndex.value].rotate = initialParams.startRotate + (deg * 180 / Math.PI) }; const stopRotate = () => { document.removeEventListener('mousemove', onRotateMove); document.removeEventListener('mouseup', stopRotate); isInteracting = false }; document.addEventListener('mousemove', onRotateMove); document.addEventListener('mouseup', stopRotate) }
const startResize = (e) => { e.stopPropagation(); isInteracting = true; startX = e.clientX; initialParams = { w: elements.value[selectedIndex.value].w, h: elements.value[selectedIndex.value].h }; const onResizeMove = (ev) => { const scale = zoom.value / 100; const newW = Math.max(50, initialParams.w + (ev.clientX - startX) / scale); const item = elements.value[selectedIndex.value]; item.w = newW; if (item.type !== 'text') item.h = newW * (initialParams.h / initialParams.w) }; const stopResize = () => { document.removeEventListener('mousemove', onResizeMove); document.removeEventListener('mouseup', stopResize); isInteracting = false }; document.addEventListener('mousemove', onResizeMove); document.addEventListener('mouseup', stopResize) }
const stopInteraction = () => { isInteracting = false; document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', stopInteraction) }
const deselectAll = () => selectedIndex.value = -1
const handleKeyDown = (e) => { if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return; if ((e.key === 'Backspace' || e.key === 'Delete') && selectedIndex.value !== -1) deleteLayer() }
const deleteLayer = () => { if (selectedIndex.value !== -1) { elements.value.splice(selectedIndex.value, 1); selectedIndex.value = -1 } }
const moveLayer = (dir) => { if (selectedIndex.value !== -1) elements.value[selectedIndex.value].zIndex += dir }
const updateText = (e, index) => { elements.value[index].text = e.target.innerHTML }
const clearCanvas = () => { elements.value = []; bgColor.value = '#ffffff'; bgImage.value = ''; saveForm.title = ''; saveForm.season = 'All Year'; saveForm.style = 'Casual'; saveForm.note = '' }
const resetView = () => zoom.value = 100

const openSaveDialog = () => {
  saveDialogVisible.value = true
}

// [核心修复] 保存逻辑：截图 -> 上传 -> 返回URL
const confirmSave = async () => {
  if (!saveForm.title) {
    ElMessage.warning('Please give your outfit a name!')
    return
  }

  isSaving.value = true
  deselectAll() // 必须取消选中，否则蓝色边框会被截进去
  
  await nextTick() // 等待 DOM 更新，去掉边框后再截图

  try {
    const artboardEl = document.getElementById('artboard')
    const canvas = await html2canvas(artboardEl, {
      useCORS: true,
      scale: 1,
      backgroundColor: null // 这里保持 null 即可实现透明
    })

    canvas.toBlob(async (blob) => {
      if (!blob) {
        ElMessage.error('Failed to generate snapshot')
        isSaving.value = false
        zoom.value = originalZoom
        return
      }

      const formData = new FormData()
      const filename = `outfit_snap_${Date.now()}.png`
      formData.append('file', blob, filename)

      try {
        const res = await request.post('/api/upload/image?type=outfit', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        // 确保 URL 是完整的或者前端能处理的
        const uploadedUrl = res.url 

        const layoutData = {
          // 传递 ID 以便父组件判断是更新
          outfit_id: props.initialData ? props.initialData.outfit_id : null,
          title: saveForm.title,
          season: saveForm.season,
          style: saveForm.style,
          note: saveForm.note,
          bg: bgColor.value,
          bgImage: bgImage.value,
          elements: JSON.parse(JSON.stringify(elements.value)), // 深度拷贝所有元素（含文字、贴纸）
          image_url: uploadedUrl
        }
        
        emit('save', layoutData)
        saveDialogVisible.value = false
      } catch (uploadErr) {
        console.error(uploadErr)
        ElMessage.error('Snapshot upload failed')
      } finally {
        isSaving.value = false
        zoom.value = originalZoom
      }
    }, 'image/png')

  } catch (err) {
    console.error('Screenshot failed', err)
    ElMessage.error('Failed to save outfit')
    isSaving.value = false
    zoom.value = originalZoom
  }
}

onMounted(async () => {
  try {
    const res = await request.get('/api/outfits/items')
    realWardrobe.value = res 
  } catch (error) {
    console.error('Failed to load items', error)
  }

  if (props.initialData) {
    saveForm.title = props.initialData.title || ''
    saveForm.note = props.initialData.note || ''
    saveForm.season = props.initialData.season || 'All Year'
    saveForm.style = props.initialData.style || 'Casual'
    
    if (props.initialData.bg) bgColor.value = props.initialData.bg
    if (props.initialData.bgImage) bgImage.value = props.initialData.bgImage

    if (props.initialData.elements && props.initialData.elements.length > 0) {
      elements.value = props.initialData.elements
      selectedIndex.value = -1 
    }
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

.studio-container {
    --primary: #6366f1;
    --surface: #ffffff;
    --bg-gray: #f3f4f6;
    --border: #e5e7eb;
    --text-main: #1f2937;
    --text-sub: #6b7280;
    
    width: 100%; height: 100%; display: flex; background-color: var(--bg-gray);
    font-family: 'Inter', sans-serif; color: var(--text-main); overflow: hidden; outline: none;
}

.studio-sidebar { width: 300px; height: 100%; background: var(--surface); display: flex; flex-direction: column; border-right: 1px solid var(--border); z-index: 20; }
.sidebar-header { padding: 24px 20px 16px; }
.header-title { font-size: 18px; font-weight: 700; color: var(--primary); }
.header-subtitle { font-size: 12px; color: var(--text-sub); }
.nav-capsules { display: flex; padding: 0 16px 16px; gap: 8px; overflow-x: auto; border-bottom: 1px solid var(--border); }
.capsule-btn { flex: 1; padding: 10px 0; border-radius: 12px; font-size: 11px; font-weight: 600; color: var(--text-sub); cursor: pointer; display: flex; flex-direction: column; align-items: center; }
.capsule-btn:hover { background: #f9fafb; color: var(--primary); }
.capsule-btn.active { background: #eef2ff; color: var(--primary); }
.capsule-btn .el-icon { font-size: 20px; margin-bottom: 4px; }
.assets-scroll-area { flex: 1; overflow-y: auto; padding: 20px; }

.category-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.cat-tag { padding: 6px 12px; background: #f3f4f6; border-radius: 20px; font-size: 12px; font-weight: 500; cursor: pointer; transition: 0.2s; }
.cat-tag:hover { background: #e2e8f0; }
.cat-tag.active { background: var(--text-main); color: white; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.grid-2-col-form { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3-col { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.asset-item { aspect-ratio: 1; background: #fff; border: 1px solid var(--border); border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: grab; }
.asset-item:hover { border-color: var(--primary); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.img-holder { width: 90%; height: 90%; display: flex; align-items: center; justify-content: center; }
.img-holder .el-image { width: 100%; height: 100%; pointer-events: none; }
.draggable-img { width: 100%; height: 100%; object-fit: contain; }

.color-palette { display: flex; flex-wrap: wrap; gap: 12px; }
.color-dot { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #ddd; cursor: pointer; }
.texture-item { font-size: 10px; font-weight: 600; color: #666; background-size: cover; }
.text-preset-card { padding: 12px; border: 1px dashed var(--border); text-align: center; margin-bottom: 8px; cursor: grab; background: #fff; }
.sticker-item img { width: 100%; height: 100%; object-fit: contain; pointer-events: none; }

.studio-workspace { flex: 1; position: relative; display: flex; flex-direction: column; background-image: radial-gradient(#cbd5e1 1px, transparent 1px); background-size: 24px 24px; }
.toolbar-island { margin: 16px 24px 0; height: 56px; background: rgba(255,255,255,0.9); backdrop-filter: blur(12px); border-radius: 16px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.6); z-index: 10; }
.left-group { display: flex; align-items: center; gap: 10px; }
.project-info { display: flex; flex-direction: column; margin-left: 8px; }
.p-name { font-weight: 600; font-size: 13px; color: #374151; }
.p-status { font-size: 10px; color: #9ca3af; }
.tools-center { display: flex; align-items: center; gap: 8px; }
.zoom-val { font-size: 12px; width: 36px; text-align: center; }
.canvas-viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: center; padding: 40px; }
.canvas-artboard { background-color: v-bind(bgColor); box-shadow: 0 20px 50px rgba(0,0,0,0.1); position: relative; user-select: none; background-size: cover;}
.empty-guide { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #cbd5e1; pointer-events: none; }

.layer-box { cursor: move; }
.layer-content img { width: 100%; height: 100%; display: block; pointer-events: none; }
.text-element { width: 100%; height: 100%; outline: none; }
.transform-controls { position: absolute; inset: -2px; pointer-events: none; }
.border-outline { width: 100%; height: 100%; border: 2px solid var(--primary); }
.control-knob { position: absolute; width: 24px; height: 24px; background: #fff; border: 1px solid var(--border); border-radius: 50%; display: flex; align-items: center; justify-content: center; pointer-events: auto; z-index: 100; cursor: pointer; color: var(--text-main); }
.rotate { top: -36px; left: 50%; transform: translateX(-50%); }
.resize-br { bottom: -12px; right: -12px; width: 16px; height: 16px; cursor: nwse-resize; background: var(--primary); border: 2px solid #fff; }

.property-floater { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.5); padding: 8px 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 16px; z-index: 50; }
.prop-section { display: flex; align-items: center; }
.divider { width: 1px; height: 20px; background: #e5e7eb; }
.label { font-size: 10px; font-weight: 700; color: #9ca3af; text-transform: uppercase; margin-right: 8px; }

.custom-dialog { border-radius: 12px; overflow: hidden; }
:deep(.el-dialog__header) { padding: 20px 24px; border-bottom: 1px solid #f3f4f6; margin-right: 0; }
:deep(.el-dialog__title) { font-family: 'Playfair Display', serif; font-weight: 700; }
:deep(.el-dialog__body) { padding: 24px; }
.no-items-tip { grid-column: 1 / -1; text-align: center; color: #9ca3af; font-size: 12px; padding: 20px; }
</style>