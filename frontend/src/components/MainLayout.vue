<script setup>
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'
</script>

<template>
  <div class="main-layout">
    <Sidebar />

    <div class="right-content">
      <TopHeader />

      <main class="page-container">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<style scoped>
.main-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #F7F8FA; /* 全局灰背景 */
  overflow: hidden; /* 防止最外层出现滚动条 */
}

.right-content {
  flex: 1; /* 占满右侧剩余空间 */
  display: flex;
  flex-direction: column;
  position: relative;
}

.page-container {
  flex: 1; /* 占满顶栏下方的所有空间 */
  overflow-y: auto; /* 内容多了，只有这里滚动，侧边栏不动 */
  padding: 0 40px 40px 40px; /* 给内容留出边距 */
}
</style>