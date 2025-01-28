<template>
  <div class="stock-positions">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>持仓管理</span>
          <div class="summary">
            <span>总市值：</span>
            <span class="value">¥{{ formatNumber(totalValue) }}</span>
            <span class="margin-left">浮动盈亏：</span>
            <span class="value" :class="totalProfit >= 0 ? 'profit' : 'loss'">
              ¥{{ formatNumber(totalProfit) }}
            </span>
          </div>
        </div>
      </template>

      <el-table :data="positions" v-loading="loading" stripe>
        <el-table-column prop="company_name" label="公司名称" />
        <el-table-column prop="shares" label="持仓数量">
          <template #default="{ row }">
            {{ formatNumber(row.shares) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价">
          <template #default="{ row }">
            ¥{{ formatNumber(row.cost_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="当前价">
          <template #default="{ row }">
            ¥{{ formatNumber(row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值">
          <template #default="{ row }">
            ¥{{ formatNumber(row.shares * row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="浮动盈亏">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'profit' : 'loss'">
              ¥{{ formatNumber(row.profit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_ratio" label="盈亏比例">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'profit' : 'loss'">
              {{ (row.profit_ratio * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToTrade(row.company_id)">
              交易
            </el-button>
            <el-button type="info" size="small" @click="viewDetail(row.company_id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'StockPositions',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const positions = ref([])

    const totalValue = computed(() => {
      return positions.value.reduce((sum, pos) => sum + pos.shares * pos.current_price, 0)
    })

    const totalProfit = computed(() => {
      return positions.value.reduce((sum, pos) => sum + pos.profit, 0)
    })

    const fetchPositions = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/stock/positions', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          positions.value = data.data
        } else {
          ElMessage.error(data.message || '获取持仓数据失败')
        }
      } catch (error) {
        console.error('获取持仓失败:', error)
        ElMessage.error('获取持仓数据失败')
      } finally {
        loading.value = false
      }
    }

    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN')
    }

    const goToTrade = (companyId) => {
      router.push(`/stock/market?company=${companyId}`)
    }

    const viewDetail = (companyId) => {
      router.push(`/company/detail/${companyId}`)
    }

    onMounted(() => {
      fetchPositions()
    })

    return {
      positions,
      loading,
      totalValue,
      totalProfit,
      formatNumber,
      goToTrade,
      viewDetail
    }
  }
}
</script>

<style scoped>
.stock-positions {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary {
  font-size: 14px;
}

.value {
  font-weight: bold;
  margin-right: 20px;
}

.margin-left {
  margin-left: 20px;
}

.profit {
  color: #67C23A;
}

.loss {
  color: #F56C6C;
}
</style> 