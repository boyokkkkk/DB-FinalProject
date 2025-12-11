<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/MainLayout.vue'

const route = useRoute()

// 这里的逻辑是：检查当前路由的 meta 信息
// 如果我们在 router/index.js 里写了 meta: { layout: 'empty' }
// 那么 isFullPage 就会变成 true
const isFullPage = computed(() => route.meta.layout === 'empty')
</script>

<template>
  <div v-if="isFullPage" class="full-page-container">
    <router-view />
  </div>

  <MainLayout v-else>
    <router-view />
  </MainLayout>
</template>

<style scoped>
.full-page-container {
  width: 100vw;
  height: 100vh;
}
</style>