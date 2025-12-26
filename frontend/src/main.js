// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import './style.css' // 默认样式，可以保留

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)){
  app.component(key, component)
}

app
  .use(router) // 使用路由
  .use(ElementPlus)
  .mount('#app')