<template>
  <div class="sidebar">
    <div class="logo-area">
      <div class="logo-icon">🧥</div>
      <h2>CLOSET OS</h2>
    </div>

    <nav class="nav-menu">
      <div class="menu-group">
        <div class="menu-title">OVERVIEW</div>
        <router-link to="/" class="menu-item" active-class="active">
          📊 Dashboard
        </router-link>
      </div>

      <div class="menu-group">
        <div class="menu-title">WARDROBE</div>
        <router-link to="/closet" class="menu-item" active-class="active">
          👗 My Closet
        </router-link>
        <router-link to="/outfit" class="menu-item" active-class="active">
          ✨ Outfit Studio
        </router-link>
      </div>

      <div class="menu-group">
        <div class="menu-title">PLANNING</div>
        <router-link to="/wishlist" class="menu-item" active-class="active">
          🎁 Wish List
        </router-link>
      </div>
    </nav>

    <div class="bottom-area">
      <div class="divider"></div>
      <router-link to="/settings" class="menu-item">
        ⚙️ Settings
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background-color: white;
  padding: 24px;
  display: flex; /* 开启 Flex */
  flex-direction: column; /* 垂直排列 */
  flex-shrink: 0; /* 禁止收缩 */
  box-sizing: border-box;
  /* position: sticky; 如果父级结构改变，这里可以不需要 sticky，交给 Layout 处理，但保留也没事 */
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 24px;
  background: #6B69F6;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.logo-area h2 {
  color: #6B69F6;
  font-size: 20px;
  margin: 0;
  font-weight: 800;
}

.nav-menu {
  flex: 1; /* 关键：占满中间所有剩余空间，把底部区域挤下去 */
}

.menu-title {
  color: #9EA3B2;
  font-size: 11px;
  margin-top: 24px;
  margin-bottom: 8px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: #5D6679;
  text-decoration: none;
  border-radius: 12px;
  margin-bottom: 4px;
  font-weight: 500;
  transition: all 0.2s;
}

.menu-item:hover {
  background-color: #F3F4F6;
  color: #333;
}

.menu-item.active {
  background-color: #6B69F6;
  color: white;
  box-shadow: 0 4px 12px rgba(107, 105, 246, 0.4);
}

.divider {
  height: 1px;
  background-color: #EEE;
  margin: 10px 0 20px 0;
}
</style>