<template>
  <div id="app">
    <GlobalLoading />
    <router-view v-slot="{ Component }">
      <component :is="Component" />
    </router-view>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { provideLoading } from './composables/useLoading'
import GlobalLoading from './components/GlobalLoading.vue'

export default {
  name: 'App',
  components: {
    GlobalLoading
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    
    provideLoading()
    
    onMounted(() => {
      // 检查登录状态
      const token = localStorage.getItem('token')
      const user = JSON.parse(localStorage.getItem('user'))
      
      if (token && user) {
        store.dispatch('login', { user, token })
      } else {
        // 如果没有登录信息，清除可能存在的残留数据
        store.dispatch('logout')
      }
    })
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 