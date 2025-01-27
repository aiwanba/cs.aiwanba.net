<template>
  <div id="app">
    <GlobalLoading />
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { provideLoading } from './composables/useLoading'
import GlobalLoading from './components/GlobalLoading.vue'

export default {
  name: 'App',
  components: {
    GlobalLoading
  },
  setup() {
    provideLoading()
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 