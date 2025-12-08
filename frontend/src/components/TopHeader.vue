<template>
  <header class="top-header">
    <div class="header-left">
      </div>

    <div class="header-right">
      <div class="user-info">
        <div class="text-info">
          <span class="name">数据库小组</span>
          <span class="role">Admin</span>
        </div>
        <div class="avatar"></div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-header {
  height: 80px; /* 固定高度 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  background-color: transparent; /* 参考图中顶栏是透明的，背景色透出 */
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.text-info {
  text-align: right;
}

.name {
  display: block;
  font-weight: bold;
  font-size: 14px;
  color: #333;
}

.role {
  display: block;
  font-size: 12px;
  color: #999;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #FDC072; /* UI图里的黄色头像 */
  border: 2px solid white;
}
</style>