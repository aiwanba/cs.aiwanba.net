<template>
  <div class="nav-container">
    <div class="logo">
      <h1>股票交易游戏</h1>
    </div>
    <div class="nav-right">
      <el-dropdown v-if="user" @command="handleCommand">
        <span class="user-info">
          {{ user.username }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const store = useStore()
const router = useRouter()
const user = computed(() => store.state.user)

const handleCommand = (command) => {
  if (command === 'logout') {
    store.dispatch('logout')
    router.push('/login')
  }
}
</script>

<style scoped>
.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 100%;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  color: white;
}

.user-info {
  color: white;
  cursor: pointer;
}
</style> 