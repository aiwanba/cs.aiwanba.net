<template>
  <div class="company-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建公司</span>
        </div>
      </template>
      
      <el-form 
        :model="formData"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        class="create-form">
        
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入公司名称" />
        </el-form-item>
        
        <el-form-item label="所属行业" prop="industry">
          <el-select v-model="formData.industry" placeholder="请选择行业">
            <el-option label="制造业" value="manufacturing" />
            <el-option label="科技" value="technology" />
            <el-option label="金融" value="finance" />
            <el-option label="服务业" value="service" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="初始股价" prop="initial_price">
          <el-input-number 
            v-model="formData.initial_price"
            :min="10"
            :max="100"
            :precision="2"
            :step="0.01" />
        </el-form-item>
        
        <el-form-item label="总股本" prop="total_shares">
          <el-input-number 
            v-model="formData.total_shares"
            :min="100000"
            :max="1000000"
            :step="10000" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            创建公司
          </el-button>
          <el-button @click="$router.push('/company/list')">取消</el-button>
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

export default {
  name: 'CompanyCreate',
  setup() {
    const router = useRouter()
    const store = useStore()
    const formRef = ref(null)
    const loading = ref(false)

    const formData = reactive({
      name: '',
      industry: '',
      initial_price: 10,
      total_shares: 100000
    })

    const rules = {
      name: [
        { required: true, message: '请输入公司名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      industry: [
        { required: true, message: '请选择所属行业', trigger: 'change' }
      ],
      initial_price: [
        { required: true, message: '请设置初始股价', trigger: 'blur' }
      ],
      total_shares: [
        { required: true, message: '请设置总股本', trigger: 'blur' }
      ]
    }

    const handleSubmit = async () => {
      try {
        await formRef.value.validate()
        loading.value = true
        
        const response = await fetch('/api/company/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...formData,
            owner_id: store.state.user.id
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('公司创建成功')
          router.push('/company/list')
        } else {
          ElMessage.error(data.error || '创建公司失败')
        }
      } catch (error) {
        ElMessage.error('创建公司失败')
      } finally {
        loading.value = false
      }
    }

    return {
      formRef,
      formData,
      rules,
      loading,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.company-create {
  padding: 20px;
}

.create-form {
  max-width: 600px;
  margin: 0 auto;
}
</style> 