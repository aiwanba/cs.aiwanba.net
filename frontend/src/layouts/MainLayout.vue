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
        <router-view />
      </main>
    </div>
    <MessageCenter />
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import SideMenu from '@/components/SideMenu.vue'
import MessageCenter from '@/components/MessageCenter.vue'
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