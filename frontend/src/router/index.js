// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
// 引入刚才创建的页面
import Dashboard from '../views/Dashboard.vue'
import MyCloset from '../views/MyCloset.vue'
import OutfitStudio from '../views/OutfitStudio.vue'
import Wishlist from '../views/Wishlist.vue'

const routes = [
  { path: '/', component: Dashboard }, // 默认显示主页
  { path: '/closet', component: MyCloset },
  { path: '/outfit', component: OutfitStudio },
  { path: '/wishlist', component: Wishlist }
  // 这里可以继续加其他页面
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router