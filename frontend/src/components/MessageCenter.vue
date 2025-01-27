<template>
  <div class="message-center">
    <el-popover
      placement="bottom-end"
      :width="300"
      trigger="click">
      <template #reference>
        <el-badge :value="unreadCount" class="message-badge">
          <el-button circle>
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
      </template>
      
      <div class="message-list">
        <div v-if="messages.length === 0" class="no-message">
          暂无消息
        </div>
        <div v-else v-for="msg in messages" :key="msg.id" class="message-item">
          <div class="message-title">{{ msg.title }}</div>
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Bell } from '@element-plus/icons-vue'

const unreadCount = ref(0)
const messages = ref([])
</script>

<style scoped>
.message-center {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 1000;
}

.message-badge {
  cursor: pointer;
}

.message-list {
  max-height: 400px;
  overflow-y: auto;
}

.message-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.message-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.message-content {
  color: #666;
  font-size: 14px;
}

.message-time {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}

.no-message {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style> 