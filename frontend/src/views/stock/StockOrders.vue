<template>
  <div class="stock-orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易订单</span>
          <el-radio-group v-model="orderType" size="small">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="active">进行中</el-radio-button>
            <el-radio-button label="completed">已完成</el-radio-button>
            <el-radio-button label="cancelled">已取消</el-radio-button>
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
        <el-table-column prop="type" label="交易类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'buy' ? 'success' : 'danger'">
              {{ row.type === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="委托价格">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="委托数量">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
        <el-table-column prop="filled_quantity" label="成交数量">
          <template #default="{ row }">
            {{ formatNumber(row.filled_quantity) }}
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
              v-if="row.status === 'active'"
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
      if (orderType.value === 'active') return orders.value.filter(o => o.status === 'active')
      if (orderType.value === 'completed') return orders.value.filter(o => o.status === 'completed')
      if (orderType.value === 'cancelled') return orders.value.filter(o => o.status === 'cancelled')
      return orders.value
    })

    const fetchOrders = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/stock/orders')
        const data = await response.json()
        
        if (response.ok) {
          orders.value = data.orders
        } else {
          ElMessage.error(data.error || '获取订单数据失败')
        }
      } catch (error) {
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
          method: 'POST'
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('订单已撤销')
          fetchOrders()
        } else {
          ElMessage.error(data.error || '撤销订单失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('撤销订单失败')
        }
      }
    }

    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN')
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const types = {
        active: 'warning',
        completed: 'success',
        cancelled: 'info'
      }
      return types[status] || 'info'
    }

    const getStatusText = (status) => {
      const texts = {
        active: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return texts[status] || status
    }

    const viewDetail = (companyId) => {
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