import { createRouter, createWebHistory } from 'vue-router'

// 引入页面
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// 懒加载其他页面
const MyCloset = () => import('../views/MyCloset.vue')
const OutfitStudio = () => import('../views/OutfitStudio.vue')
const Wishlist = () => import('../views/Wishlist.vue')
const Settings = () => import('../views/Settings.vue') // [新增]

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'empty' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { layout: 'empty' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  { path: '/closet', name: 'MyCloset', component: MyCloset },
  { path: '/outfit', name: 'OutfitStudio', component: OutfitStudio },
  { path: '/wishlist', name: 'Wishlist', component: Wishlist },
  { path: '/settings', name: 'Settings', component: Settings } // [新增]
]

// ... (后面的 router.beforeEach 和 export default router 保持不变)
const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userInfo = localStorage.getItem('user_info')
  if (to.name === 'Login' || to.name === 'Register') {
    next()
    return
  }
  if (!userInfo) {
    next('/login')
  } else {
    next()
  }
})

export default router