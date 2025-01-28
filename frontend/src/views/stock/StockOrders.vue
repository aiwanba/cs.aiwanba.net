<template>
  <div class="stock-orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易订单</span>
          <el-radio-group v-model="orderType" size="small">
            <el-radio-button :value="'all'">全部</el-radio-button>
            <el-radio-button :value="'active'">进行中</el-radio-button>
            <el-radio-button :value="'completed'">已完成</el-radio-button>
            <el-radio-button :value="'cancelled'">已取消</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="filteredOrders" v-loading="loading" stripe>
        <el-table-column prop="created_at" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="公司名称" />
        <el-table-column prop="order_type" label="交易类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.order_type === 'buy' ? 'success' : 'danger'">
              {{ row.order_type === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="委托价格">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="委托数量">
          <template #default="{ row }">
            {{ formatNumber(row.amount || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'"
              type="danger" 
              size="small" 
              @click="cancelOrder(row.id)">
              撤单
            </el-button>
            <el-button 
              type="primary" 
              size="small" 
              @click="viewDetail(row.company_id)">
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
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'StockOrders',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const orders = ref([])
    const orderType = ref('all')

    const filteredOrders = computed(() => {
      if (orderType.value === 'all') return orders.value
      return orders.value.filter(o => o.status === orderType.value)
    })

    const fetchOrders = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/stock/orders', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          orders.value = data.data
        } else {
          ElMessage.error(data.message || '获取订单数据失败')
        }
      } catch (error) {
        console.error('获取订单失败:', error)
        ElMessage.error('获取订单数据失败')
      } finally {
        loading.value = false
      }
    }

    const cancelOrder = async (orderId) => {
      try {
        await ElMessageBox.confirm('确定要撤销这笔订单吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await fetch(`/api/stock/orders/${orderId}/cancel`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('订单已撤销')
          fetchOrders()
        } else {
          ElMessage.error(data.message || '撤销订单失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('撤销订单失败:', error)
          ElMessage.error('撤销订单失败')
        }
      }
    }

    const formatNumber = (num) => {
      if (num === undefined || num === null) return '0'
      return Number(num).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const types = {
        pending: 'warning',
        completed: 'success',
        cancelled: 'info'
      }
      return types[status] || 'info'
    }

    const getStatusText = (status) => {
      const texts = {
        pending: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return texts[status] || status
    }

    const viewDetail = (companyId) => {
      if (!companyId) {
        ElMessage.warning('无效的公司ID')
        return
      }
      router.push(`/company/detail/${companyId}`)
    }

    onMounted(() => {
      fetchOrders()
    })

    return {
      orders,
      loading,
      orderType,
      filteredOrders,
      formatNumber,
      formatDate,
      getStatusType,
      getStatusText,
      cancelOrder,
      viewDetail
    }
  }
}
</script>

<style scoped>
.stock-orders {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 