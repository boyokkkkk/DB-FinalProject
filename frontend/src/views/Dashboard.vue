<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import request from '../utils/request' // 引入封装好的请求工具

const router = useRouter()
const username = ref('User')
const chartRef = ref(null)
let myChart = null

// ==========================================
// 1. 数据状态 (Reactive Data)
// ==========================================

// 核心统计数据 (默认值为 0，图标和颜色保持不变)
const stats = ref([
  { title: '单品总数', value: 0, icon: '🧥', bg: '#ECECFE', color: '#6B69F6' },
  { title: '搭配方案', value: 0, icon: '✨', bg: '#FFF7E6', color: '#FFC069' },
  { title: '心愿清单', value: 0, icon: '🎁', bg: '#FFEFF0', color: '#FF4D4F' },
  { title: '总花费', value: '¥ 0', icon: '💰', bg: '#E6FFFB', color: '#5CDBD3' },
])

// 饼图数据 (分类占比)
const categoryData = ref([])

// 最近添加的单品
const recentItems = ref([])

// ==========================================
// 2. 辅助函数
// ==========================================

// 将后端时间转为 "xxx前" 的格式
const timeAgo = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)

  if (seconds < 60) return '刚刚'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return dateString.split('T')[0] // 超过30天显示日期
}

// 颜色映射 (给最近单品的占位图一点颜色)
const getCategoryColor = (catName) => {
  const map = {
    '上装': '#E3E8F0', '下装': '#F0F0F0', '外套': '#D4C4B7',
    '鞋子': '#333333', '连衣裙': '#FFEFF0', '配饰': '#FFC069'
  }
  return map[catName] || '#ECECFE'
}

// ==========================================
// 3. 核心逻辑 & 图表
// ==========================================

// 初始化图表
const initChart = () => {
  if (myChart) myChart.dispose() // 防止重复初始化
  myChart = echarts.init(chartRef.value)

  const option = {
    tooltip: { trigger: 'item' },
    legend: {
      bottom: '0', left: 'center', icon: 'circle', itemGap: 10,
      textStyle: { fontSize: 12, color: '#666' }
    },
    color: ['#6B69F6', '#9492F8', '#BDBBFB', '#E2E1FD', '#F0F0F5', '#FF9F7F'],
    series: [
      {
        name: '衣橱分布',
        type: 'pie',
        radius: ['35%', '55%'],
        center: ['50%', '40%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#333' }
        },
        // 如果没有数据，显示一个灰色的空圆环
        data: categoryData.value.length ? categoryData.value : [{value: 1, name: '暂无数据', itemStyle: {color: '#eee'}}]
      }
    ]
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}

// 加载所有数据
const fetchAllData = async () => {
  try {
    // 1. 请求衣橱统计 (总数、总价、分类、最近单品)
    const dashRes = await request.get('/api/closet/dashboard/stats')
    // 2. 请求搭配列表 (为了算个数)
    const outfitRes = await request.get('/api/outfits/')
    // 3. 请求心愿单统计
    const wishRes = await request.get('/api/wishlist/stats')

    // --- 更新 Stats 卡片 ---
    stats.value[0].value = dashRes.total_count
    stats.value[1].value = outfitRes.length
    stats.value[2].value = wishRes.total_items
    // 格式化金额，保留0位小数并加千分位
    stats.value[3].value = `¥ ${dashRes.total_price.toLocaleString('en-US', {maximumFractionDigits: 0})}`

    // --- 更新分类图表 ---
    categoryData.value = dashRes.category_data
    initChart() // 数据拿到后重绘图表

    // --- 更新最近列表 ---
    // 这里需要处理一下数据格式以适配模板
    recentItems.value = dashRes.recent_items.map(item => ({
      id: item.item_id,
      name: item.name,
      date: timeAgo(item.created_at),
      // 注意：这里需要后端返回 category 名字，但我们的 recent_items 查询没连表
      // 简单处理：如果后端没返回 category 名字，就标为 '单品'
      // *更完美的做法是后端 recent_items 应该做 join 查询，但为了简单，这里先这样*
      tag: '新购入',
      color: getCategoryColor(item.color) // 尝试用颜色名字匹配背景色
    }))

  } catch (error) {
    console.error("加载仪表盘数据失败:", error)
  }
}

// 生命周期
onMounted(() => {
  // 读取用户名
  const stored = localStorage.getItem('user_info')
  if (stored) {
    username.value = JSON.parse(stored).username
  }

  // 初始化空图表
  nextTick(() => {
    initChart()
    // 开始拉取真实数据
    fetchAllData()
  })
})

// 快捷跳转
const go = (path) => {
  router.push(path)
}
</script>
<template>
  <div class="dashboard-container">
    <div class="welcome-section">
      <h1>嗨, {{ username }} ✨</h1>
      <p>准备好今天的搭配了吗？</p>
    </div>

    <div class="stats-grid">
      <div
        v-for="(item, index) in stats"
        :key="index"
        class="stat-card"
      >
        <div class="stat-icon" :style="{ background: item.bg, color: item.color }">
          {{ item.icon }}
        </div>
        <div class="stat-info">
          <span class="stat-value" :style="{ color: item.color }">{{ item.value }}</span>
          <span class="stat-title">{{ item.title }}</span>
        </div>
      </div>
    </div>

    <div class="main-content-grid">

      <div class="content-card chart-card">
        <div class="card-header">
          <h3>衣橱分类占比</h3>
          <span class="tag">Category</span>
        </div>
        <div class="chart-container" ref="chartRef"></div>
      </div>

      <div class="content-card list-card">
        <div class="card-header">
          <h3>最近添加</h3>
          <button class="link-btn" @click="go('/closet')">查看全部</button>
        </div>

        <div class="recent-list">
          <div v-for="item in recentItems" :key="item.id" class="list-item">
            <div class="item-img-placeholder" :style="{ background: item.color }"></div>
            <div class="item-info">
              <h4>{{ item.name }}</h4>
              <span class="item-date">{{ item.date }} · {{ item.tag }}</span>
            </div>
            <button class="mini-btn">></button>
          </div>
        </div>
      </div>

    </div>

    <div class="quick-actions">
      <h3>快捷操作</h3>
      <div class="action-buttons">
        <button class="action-btn primary" @click="go('/closet')">
          <span>+</span> 添加新单品
        </button>
        <button class="action-btn outline" @click="go('/outfit')">
          <span>✨</span> 创建搭配
        </button>
        <button class="action-btn outline" @click="go('/wishlist')">
          <span>❤️</span> 添加心愿
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 0 20px 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎区 */
.welcome-section {
  margin-bottom: 30px;
}
.welcome-section h1 {
  font-size: 28px;
  margin: 0 0 8px 0;
  color: #333;
}
.welcome-section p {
  color: #999;
  margin: 0;
  font-size: 14px;
}

/* 核心指标 Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4列等宽 */
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.06);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
}

.stat-title {
  color: #999;
  font-size: 13px;
  margin-top: 4px;
}

/* 主要内容 Grid */
.main-content-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr; /* 左边图表稍微宽一点 */
  gap: 20px;
  margin-bottom: 30px;
}

.content-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.tag {
  background: #F2F3F5;
  color: #666;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.link-btn {
  background: none;
  border: none;
  color: #6B69F6;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 250px; /* 固定高度确保图表能显示 */
}

/* 列表样式 */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f7f7f7;
}

.list-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.item-img-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background-color: #eee;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.item-date {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  display: block;
}

.mini-btn {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
}

/* 快捷操作 */
.quick-actions h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.action-btn {
  padding: 14px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.action-btn.primary {
  background-color: #6B69F6;
  color: white;
  border: none;
  box-shadow: 0 4px 10px rgba(107, 105, 246, 0.3);
}

.action-btn.primary:hover {
  background-color: #5a58d6;
  transform: translateY(-2px);
}

.action-btn.outline {
  background-color: white;
  border: 1px solid #E0E0E0;
  color: #555;
}

.action-btn.outline:hover {
  border-color: #6B69F6;
  color: #6B69F6;
  background-color: #F8F8FF;
}

/* 响应式调整 */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr); /* 屏幕窄时变2列 */
  }
  .main-content-grid {
    grid-template-columns: 1fr; /* 屏幕窄时变单列 */
  }
}
</style>