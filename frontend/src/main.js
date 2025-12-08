// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import './style.css' // 默认样式，可以保留

createApp(App)
  .use(router) // 挂载路由
  .mount('#app')