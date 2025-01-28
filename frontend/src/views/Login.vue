<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>用户登录</h2>
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px">
        
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="formData.username"
            placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="formData.password"
            type="password"
            placeholder="请输入密码" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">
            登录
          </el-button>
          <el-button @click="$router.push('/register')">
            注册账号
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import auth from '../services/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const store = useStore()
    const formRef = ref(null)
    const loading = ref(false)

    const formData = reactive({
      username: '',
      password: ''
    })

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      try {
        await formRef.value.validate()
        loading.value = true
        
        const requestData = {
          username: formData.username,
          password: formData.password
        }
        
        console.log('Sending login request:', requestData)
        const response = await auth.login(requestData)
        console.log('Raw response:', response)
        
        if (response && response.token) {
          store.dispatch('login', {
            user: response.user,
            token: response.token
          })
          ElMessage.success(response.message || '登录成功')
          router.push('/dashboard')
        } else {
          console.error('Invalid response format:', response)
          throw new Error('登录响应数据格式错误')
        }
      } catch (error) {
        console.error('Login error:', error)
        console.error('Error response:', error.response)
        ElMessage.error(error.response?.data?.message || '登录失败')
      } finally {
        loading.value = false
      }
    }

    return {
      formRef,
      formData,
      rules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.el-form {
  margin-top: 20px;
}

.el-button {
  width: 100%;
  margin-bottom: 10px;
}
</style> 