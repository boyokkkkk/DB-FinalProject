// 注意：这个文件必须放在 frontend 根目录（和 src 文件夹同级）
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import { fileURLToPath } from 'url';

// 解决 Node.js ES 模块下 __dirname 未定义的问题（Vite 默认为 ES 模块）
const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 关键：@ 指向 src 目录（绝对路径，避免相对路径坑）
      '@': path.resolve(__dirname, './src') 
    },
    // 可选：添加扩展名解析，避免导入时漏写 .vue/.js
    extensions: ['.mjs', '.js', '.jsx', '.json', '.vue']
  },
  server: {
    port: 5173, // 前端端口（默认）
    open: true, // 启动后自动打开浏览器
    proxy: {
      // 跨域代理（前端请求 /api 会转发到后端 3001）
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});