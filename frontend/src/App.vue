<script setup>
import MainLayout from './components/MainLayout.vue' // 假设你放在 layouts 文件夹
// 如果放在 components 文件夹，路径就是 './components/MainLayout.vue'
</script>

<template>
  <MainLayout>
    <router-view />
  </MainLayout>
</template>

<style>
/* App.vue 里只需要留一些全局的基础样式，或者直接留空 */
</style>