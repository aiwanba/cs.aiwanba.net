<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>

      <el-form :model="settings" :rules="rules" ref="settingsFormRef" label-width="120px">
        <!-- 通知设置 -->
        <el-divider>通知设置</el-divider>
        <el-form-item label="系统通知" prop="notifications.system">
          <el-switch v-model="settings.notifications.system" />
        </el-form-item>
        <el-form-item label="交易提醒" prop="notifications.trade">
          <el-switch v-model="settings.notifications.trade" />
        </el-form-item>
        <el-form-item label="声音提醒" prop="notifications.sound">
          <el-switch v-model="settings.notifications.sound" />
        </el-form-item>

        <!-- 显示设置 -->
        <el-divider>显示设置</el-divider>
        <el-form-item label="主题模式" prop="display.theme">
          <el-radio-group v-model="settings.display.theme">
            <el-radio label="light">浅色</el-radio>
            <el-radio label="dark">深色</el-radio>
            <el-radio label="auto">跟随系统</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="表格密度" prop="display.tableSize">
          <el-radio-group v-model="settings.display.tableSize">
            <el-radio label="large">宽松</el-radio>
            <el-radio label="default">默认</el-radio>
            <el-radio label="small">紧凑</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 安全设置 -->
        <el-divider>安全设置</el-divider>
        <el-form-item label="自动锁定" prop="security.autoLock">
          <el-switch v-model="settings.security.autoLock" />
        </el-form-item>
        <el-form-item label="锁定时间" prop="security.lockTime" v-if="settings.security.autoLock">
          <el-select v-model="settings.security.lockTime">
            <el-option label="5分钟" value="5" />
            <el-option label="10分钟" value="10" />
            <el-option label="30分钟" value="30" />
            <el-option label="1小时" value="60" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="loading">
            保存设置
          </el-button>
          <el-button @click="resetSettings">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'SystemSettings',
  setup() {
    const loading = ref(false)
    const settingsFormRef = ref(null)

    const defaultSettings = {
      notifications: {
        system: true,
        trade: true,
        sound: true
      },
      display: {
        theme: 'light',
        tableSize: 'default'
      },
      security: {
        autoLock: false,
        lockTime: '30'
      }
    }

    const settings = ref({ ...defaultSettings })

    const rules = {
      'notifications.system': [
        { required: true, message: '请选择是否开启系统通知', trigger: 'change' }
      ],
      'notifications.trade': [
        { required: true, message: '请选择是否开启交易提醒', trigger: 'change' }
      ],
      'display.theme': [
        { required: true, message: '请选择主题模式', trigger: 'change' }
      ],
      'display.tableSize': [
        { required: true, message: '请选择表格密度', trigger: 'change' }
      ]
    }

    const fetchSettings = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/settings')
        const data = await response.json()
        
        if (response.ok) {
          settings.value = { ...defaultSettings, ...data.settings }
        } else {
          ElMessage.error(data.error || '获取设置失败')
        }
      } catch (error) {
        ElMessage.error('获取设置失败')
      } finally {
        loading.value = false
      }
    }

    const saveSettings = async () => {
      try {
        await settingsFormRef.value.validate()
        
        loading.value = true
        const response = await fetch('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings.value)
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('设置保存成功')
          // 应用设置
          applySettings(settings.value)
        } else {
          ElMessage.error(data.error || '保存设置失败')
        }
      } catch (error) {
        if (error.message) {
          ElMessage.error(error.message)
        }
      } finally {
        loading.value = false
      }
    }

    const resetSettings = () => {
      settings.value = { ...defaultSettings }
      ElMessage.success('设置已重置')
    }

    const applySettings = (newSettings) => {
      // 应用主题
      document.documentElement.setAttribute('data-theme', newSettings.display.theme)
      // 应用表格密度
      document.documentElement.style.setProperty('--el-table-row-height', 
        newSettings.display.tableSize === 'small' ? '32px' : 
        newSettings.display.tableSize === 'large' ? '48px' : '40px'
      )
    }

    onMounted(() => {
      fetchSettings()
    })

    return {
      loading,
      settings,
      settingsFormRef,
      rules,
      saveSettings,
      resetSettings
    }
  }
}
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-divider__text) {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}
</style> 