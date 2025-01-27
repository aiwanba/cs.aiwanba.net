<template>
  <div class="company-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>公司列表</span>
          <el-button type="primary" @click="$router.push('/company/create')">
            创建公司
          </el-button>
        </div>
      </template>
      
      <el-table :data="companies" v-loading="loading">
        <el-table-column prop="name" label="公司名称" />
        <el-table-column prop="industry" label="所属行业" />
        <el-table-column prop="total_shares" label="总股本">
          <template #default="{ row }">
            {{ formatNumber(row.total_shares) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="当前股价">
          <template #default="{ row }">
            ¥{{ formatNumber(row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值">
          <template #default="{ row }">
            ¥{{ formatNumber(row.total_shares * row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row.id)">
              详情
            </el-button>
            <el-button type="success" size="small" @click="goToTrade(row.id)">
              交易
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'CompanyList',
  setup() {
    const router = useRouter()
    const companies = ref([])
    const loading = ref(false)

    const fetchCompanies = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/company/list')
        const data = await response.json()
        
        if (response.ok) {
          companies.value = data.companies
        } else {
          ElMessage.error(data.error || '获取公司列表失败')
        }
      } catch (error) {
        ElMessage.error('获取公司列表失败')
      } finally {
        loading.value = false
      }
    }

    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN')
    }

    const viewDetail = (id) => {
      router.push(`/company/detail/${id}`)
    }

    const goToTrade = (id) => {
      router.push(`/stock/market?company=${id}`)
    }

    onMounted(() => {
      fetchCompanies()
    })

    return {
      companies,
      loading,
      formatNumber,
      viewDetail,
      goToTrade
    }
  }
}
</script>

<style scoped>
.company-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 