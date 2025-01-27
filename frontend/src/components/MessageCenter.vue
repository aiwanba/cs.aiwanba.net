<template>
  <div class="message-center">
    <el-popover
      placement="bottom-end"
      :width="350"
      trigger="click"
      popper-class="message-popover"
    >
      <template #reference>
        <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="message-badge">
          <el-button circle>
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
      </template>

      <template #default>
        <div class="message-header">
          <span>消息中心</span>
          <el-button link type="primary" @click="markAllRead" :disabled="!hasUnread">
            全部已读
          </el-button>
        </div>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="系统通知" name="system">
            <div v-if="systemMessages.length" class="message-list">
              <div
                v-for="msg in systemMessages"
                :key="msg.id"
                class="message-item"
                :class="{ unread: !msg.read }"
                @click="handleMessageClick(msg)"
              >
                <div class="message-title">
                  <span>{{ msg.title }}</span>
                  <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                </div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无系统通知" />
          </el-tab-pane>

          <el-tab-pane label="交易提醒" name="trade">
            <div v-if="tradeMessages.length" class="message-list">
              <div
                v-for="msg in tradeMessages"
                :key="msg.id"
                class="message-item"
                :class="{ unread: !msg.read }"
                @click="handleMessageClick(msg)"
              >
                <div class="message-title">
                  <span>{{ msg.title }}</span>
                  <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                </div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无交易提醒" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-popover>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useWebSocket } from '../composables/useWebSocket'

export default {
  name: 'MessageCenter',
  components: { Bell },
  setup() {
    const activeTab = ref('system')
    const messages = ref([])
    const { connect, disconnect } = useWebSocket()

    const systemMessages = computed(() => 
      messages.value.filter(msg => msg.type === 'system')
    )

    const tradeMessages = computed(() => 
      messages.value.filter(msg => msg.type === 'trade')
    )

    const unreadCount = computed(() => 
      messages.value.filter(msg => !msg.read).length
    )

    const hasUnread = computed(() => unreadCount.value > 0)

    const fetchMessages = async () => {
      try {
        const response = await fetch('/api/messages')
        const data = await response.json()
        
        if (response.ok) {
          messages.value = data.messages
        } else {
          ElMessage.error(data.error || '获取消息失败')
        }
      } catch (error) {
        ElMessage.error('获取消息失败')
      }
    }

    const handleMessageClick = async (message) => {
      if (!message.read) {
        try {
          const response = await fetch(`/api/messages/${message.id}/read`, {
            method: 'POST'
          })
          
          if (response.ok) {
            message.read = true
          }
        } catch (error) {
          console.error('标记消息已读失败:', error)
        }
      }
    }

    const markAllRead = async () => {
      try {
        const response = await fetch('/api/messages/read-all', {
          method: 'POST'
        })
        
        if (response.ok) {
          messages.value.forEach(msg => msg.read = true)
          ElMessage.success('已全部标记为已读')
        } else {
          ElMessage.error('标记已读失败')
        }
      } catch (error) {
        ElMessage.error('标记已读失败')
      }
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date

      if (diff < 60000) { // 小于1分钟
        return '刚刚'
      } else if (diff < 3600000) { // 小于1小时
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 小于24小时
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return date.toLocaleString('zh-CN')
      }
    }

    onMounted(() => {
      fetchMessages()
      connect()
    })

    onUnmounted(() => {
      disconnect()
    })

    return {
      activeTab,
      messages,
      systemMessages,
      tradeMessages,
      unreadCount,
      hasUnread,
      handleMessageClick,
      markAllRead,
      formatTime
    }
  }
}
</script>

<style scoped>
.message-center {
  display: inline-block;
}

.message-badge {
  margin-right: 16px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #EBEEF5;
}

.message-list {
  max-height: 300px;
  overflow-y: auto;
}

.message-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #EBEEF5;
}

.message-item:hover {
  background-color: #F5F7FA;
}

.message-item.unread {
  background-color: #F0F9EB;
}

.message-title {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  font-size: 13px;
  color: #606266;
}
</style> 