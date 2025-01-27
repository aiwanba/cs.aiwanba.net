<template>
  <el-container class="app-container">
    <el-header>
      <nav-bar></nav-bar>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <side-menu></side-menu>
      </el-aside>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import NavBar from './components/NavBar.vue'
import SideMenu from './components/SideMenu.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    SideMenu
  }
}
</script>

<style>
.app-container {
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
}

.el-aside {
  background-color: #f8f9fa;
}
</style> 