<template>
  <div class="nav-container">
    <div class="logo">
      <h1>股票交易游戏</h1>
    </div>
    <div class="nav-right">
      <el-dropdown v-if="user" @command="handleCommand">
        <span class="user-info">
          {{ user.username }}
          <el-icon><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人信息</el-dropdown-item>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'NavBar',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const user = computed(() => store.state.user)
    
    const handleCommand = (command) => {
      if (command === 'logout') {
        localStorage.removeItem('token')
        store.commit('setUser', null)
        router.push('/login')
        ElMessage.success('已退出登录')
      } else if (command === 'profile') {
        router.push('/profile')
      }
    }
    
    return {
      user,
      handleCommand
    }
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