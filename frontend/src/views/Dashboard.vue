<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts' // 引入图表库

const router = useRouter()
const username = ref('User')

// ==========================================
// 1. 模拟数据 (MOCK DATA)
// 以后连接数据库时，只需要把这些 ref 的值替换成 API 返回的数据即可
// ==========================================

// 核心统计数据
const stats = ref([
  { title: '单品总数', value: 128, icon: '🧥', bg: '#ECECFE', color: '#6B69F6' },
  { title: '搭配方案', value: 45, icon: '✨', bg: '#FFF7E6', color: '#FFC069' },
  { title: '心愿清单', value: 12, icon: '🎁', bg: '#FFEFF0', color: '#FF4D4F' },
  { title: '总花费', value: '¥ 8,500', icon: '💰', bg: '#E6FFFB', color: '#5CDBD3' },
])

// 饼图数据 (分类占比)
const categoryData = [
  { value: 48, name: '上装 Tops' },
  { value: 35, name: '下装 Bottoms' },
  { value: 24, name: '鞋履 Shoes' },
  { value: 12, name: '配饰 Acc' },
  { value: 9,  name: '外套 Outer' }
]

// 最近添加的单品 (图片先用颜色块代替，你可以换成真实URL)
const recentItems = ref([
  { id: 1, name: '白色棉质衬衫', date: '2小时前', tag: '上装', color: '#F0F0F0' },
  { id: 2, name: '复古牛仔裤', date: '5小时前', tag: '下装', color: '#E3E8F0' },
  { id: 3, name: '黑色切尔西靴', date: '1天前', tag: '鞋履', color: '#333333' },
  { id: 4, name: '羊毛围巾', date: '2天前', tag: '配饰', color: '#D4C4B7' },
])

// ==========================================
// 2. 逻辑处理
// ==========================================

// 初始化图表
const chartRef = ref(null)

const initChart = () => {
  const myChart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '0',        // 放在底部
      left: 'center',     // 居中
      icon: 'circle',     // 圆形图标
      itemGap: 10,        // 图例之间的间距
      textStyle: {
        fontSize: 12,
        color: '#666'
      }
    },
    color: ['#6B69F6', '#9492F8', '#BDBBFB', '#E2E1FD', '#F0F0F5'],
    series: [
      {
        name: '衣橱分布',
        type: 'pie',
        // 🟢 修改点 1：半径稍微改小一点，留出呼吸感
        radius: ['35%', '55%'],
        // 🟢 修改点 2：把圆心向上移动 (X轴 50%, Y轴 40%)，默认为 50%
        center: ['50%', '40%'],

        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#333'
          }
        },
        data: categoryData
      }
    ]
  }

  myChart.setOption(option)

  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

// 获取用户信息 & 初始化
onMounted(() => {
  // 读取用户名
  const stored = localStorage.getItem('user_info')
  if (stored) {
    username.value = JSON.parse(stored).username
  }

  // 渲染图表
  nextTick(() => {
    initChart()
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