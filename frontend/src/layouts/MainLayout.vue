<template>
  <div class="layout">
    <header class="header">
      <NavBar />
    </header>
    <div class="container">
      <aside class="sidebar">
        <SideMenu />
      </aside>
      <main class="main">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
    <MessageCenter />
  </div>
</template>

<script setup>
import { onBeforeUnmount } from 'vue'
import NavBar from '../components/NavBar.vue'
import SideMenu from '../components/SideMenu.vue'
import MessageCenter from '../components/MessageCenter.vue'

onBeforeUnmount(() => {
  // 清理可能的副作用
})
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  height: 60px;
  background: #409EFF;
}

.container {
  flex: 1;
  display: flex;
}

.sidebar {
  width: 200px;
  background: #f5f7fa;
}

.main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style> 