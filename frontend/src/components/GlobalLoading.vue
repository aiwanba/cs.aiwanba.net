<template>
  <div v-if="isLoading" class="global-loading">
    <div class="loading-content">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span class="loading-text">{{ loadingText }}</span>
    </div>
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'
import { useLoading } from '../composables/useLoading'

export default {
  name: 'GlobalLoading',
  components: { Loading },
  setup() {
    const { isLoading, loadingText } = useLoading()

    return {
      isLoading,
      loadingText
    }
  }
}
</script>

<style scoped>
.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  font-size: 48px;
  color: var(--el-color-primary);
  animation: rotate 1s linear infinite;
}

.loading-text {
  font-size: 16px;
  color: var(--el-text-color-primary);
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 