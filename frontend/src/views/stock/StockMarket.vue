<template>
  <div class="stock-market">
    <!-- 添加公司选择 -->
    <el-card v-if="!selectedCompany" class="company-select">
      <template #header>
        <div class="card-header">
          <span>选择交易公司</span>
        </div>
      </template>
      
      <el-table :data="companies" stripe>
        <el-table-column prop="name" label="公司名称" />
        <el-table-column prop="current_price" label="当前股价">
          <template #default="{ row }">
            ¥{{ formatNumber(row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="primary" @click="selectCompany(row)">
              选择
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 原有的交易界面，添加v-else -->
    <div v-else>
      <el-row :gutter="20">
        <!-- 左侧交易区域 -->
        <el-col :span="16">
          <el-card class="trade-card">
            <template #header>
              <div class="card-header">
                <div class="company-info">
                  <h3>{{ company.name }}</h3>
                  <div class="price-info">
                    <span class="current-price" :class="priceChangeClass">
                      ¥{{ formatNumber(company.current_price) }}
                    </span>
                    <span class="price-change" :class="priceChangeClass">
                      {{ formatPriceChange(company.price_change) }}
                    </span>
                  </div>
                </div>
              </div>
            </template>

            <!-- 交易表单 -->
            <el-form :model="tradeForm" :rules="rules" ref="tradeFormRef" label-width="80px">
              <el-form-item label="交易类型">
                <el-radio-group v-model="tradeForm.type">
                  <el-radio label="buy">买入</el-radio>
                  <el-radio label="sell">卖出</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="价格" prop="price">
                <el-input-number 
                  v-model="tradeForm.price"
                  :min="0.01"
                  :precision="2"
                  :step="0.01"
                  style="width: 200px" />
              </el-form-item>

              <el-form-item label="数量" prop="quantity">
                <el-input-number 
                  v-model="tradeForm.quantity"
                  :min="100"
                  :step="100"
                  style="width: 200px" />
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  :loading="loading"
                  @click="submitTrade">
                  {{ tradeForm.type === 'buy' ? '买入' : '卖出' }}
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 交易明细 -->
            <div class="trade-details">
              <div class="detail-item">
                <span>交易总额</span>
                <span>¥{{ formatNumber(tradeForm.price * tradeForm.quantity) }}</span>
              </div>
              <div class="detail-item">
                <span>手续费</span>
                <span>¥{{ formatNumber(calculateFee()) }}</span>
              </div>
              <div class="detail-item total">
                <span>实际金额</span>
                <span>¥{{ formatNumber(calculateTotal()) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧订单簿 -->
        <el-col :span="8">
          <el-card class="order-book">
            <template #header>
              <div class="card-header">
                <span>订单簿</span>
              </div>
            </template>

            <!-- 卖单列表 -->
            <div class="sell-orders">
              <div v-for="order in sellOrders" :key="order.id" class="order-item sell">
                <span class="price">¥{{ formatNumber(order.price) }}</span>
                <span class="quantity">{{ formatNumber(order.quantity) }}</span>
              </div>
            </div>

            <!-- 买单列表 -->
            <div class="buy-orders">
              <div v-for="order in buyOrders" :key="order.id" class="order-item buy">
                <span class="price">¥{{ formatNumber(order.price) }}</span>
                <span class="quantity">{{ formatNumber(order.quantity) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近成交 -->
      <el-card class="recent-trades">
        <template #header>
          <div class="card-header">
            <span>最近成交</span>
          </div>
        </template>

        <el-table :data="recentTrades" stripe>
          <el-table-column prop="time" label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.time) }}
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格">
            <template #default="{ row }">
              ¥{{ formatNumber(row.price) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量">
            <template #default="{ row }">
              {{ formatNumber(row.quantity) }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型">
            <template #default="{ row }">
              <el-tag :type="row.type === 'buy' ? 'success' : 'danger'">
                {{ row.type === 'buy' ? '买入' : '卖出' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { io } from 'socket.io-client'
import { formatNumber, formatDate } from '@/utils/format'

export default {
  name: 'StockMarket',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const socket = io(import.meta.env.VITE_WS_URL || 'http://localhost:5010', {
      path: '/socket.io',
      transports: ['websocket'],
      autoConnect: false,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })
    const loading = ref(false)
    const tradeFormRef = ref(null)
    
    const company = ref({})
    const sellOrders = ref([])
    const buyOrders = ref([])
    const recentTrades = ref([])
    const companies = ref([])
    const selectedCompany = ref(null)

    const tradeForm = reactive({
      type: 'buy',
      price: 0,
      quantity: 100
    })

    const rules = {
      price: [
        { required: true, message: '请输入交易价格', trigger: 'blur' }
      ],
      quantity: [
        { required: true, message: '请输入交易数量', trigger: 'blur' }
      ]
    }

    // 计算价格变化的样式类
    const priceChangeClass = computed(() => {
      if (!company.value.price_change) return ''
      return company.value.price_change >= 0 ? 'price-up' : 'price-down'
    })

    // 格式化价格变化
    const formatPriceChange = (change) => {
      if (!change) return '0.00%'
      const sign = change >= 0 ? '+' : ''
      return `${sign}${(change * 100).toFixed(2)}%`
    }

    // 计算手续费
    const calculateFee = () => {
      const amount = tradeForm.price * tradeForm.quantity
      return amount * 0.001 // 0.1% 手续费
    }

    // 计算总金额
    const calculateTotal = () => {
      const amount = tradeForm.price * tradeForm.quantity
      const fee = calculateFee()
      return tradeForm.type === 'buy' ? amount + fee : amount - fee
    }

    // 获取公司数据
    const fetchCompanyData = async () => {
      try {
        // 从路由查询参数获取公司ID
        const companyId = route.query.company
        if (!companyId) {
          ElMessage.error('未指定公司ID')
          return
        }

        loading.value = true
        const response = await fetch(`/api/company/${companyId}`)
        const data = await response.json()
        
        if (response.ok) {
          company.value = data.data // 注意这里要访问 data.data
          tradeForm.price = company.value.current_price
        } else {
          ElMessage.error(data.message || '获取公司数据失败')
        }
      } catch (error) {
        console.error('获取公司数据失败:', error)
        ElMessage.error('获取公司数据失败')
      } finally {
        loading.value = false
      }
    }

    // 获取公司列表
    const fetchCompanies = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/stock/market', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          companies.value = data.data
        } else {
          ElMessage.error(data.message || '获取公司列表失败')
        }
      } catch (error) {
        console.error('获取公司列表失败:', error)
        ElMessage.error('获取公司列表失败')
      } finally {
        loading.value = false
      }
    }

    // 选择公司
    const selectCompany = (company) => {
      selectedCompany.value = company
      // 更新路由参数
      router.replace({
        query: { ...route.query, company: company.id }
      })
    }

    // 修改 WebSocket 监听器初始化
    const initSocketListeners = () => {
      // 连接事件处理
      socket.on('connect', () => {
        console.log('WebSocket connected')
        const companyId = route.query.company
        if (companyId) {
          socket.emit('subscribe', { company_id: companyId })
        }
      })

      // 连接错误处理
      socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        ElMessage.error('实时数据连接失败，正在重试...')
      })

      // 重连事件处理
      socket.on('reconnect', (attemptNumber) => {
        console.log('WebSocket reconnected after', attemptNumber, 'attempts')
        const companyId = route.query.company
        if (companyId) {
          socket.emit('subscribe', { company_id: companyId })
        }
      })

      // 价格更新
      socket.on('price_update', (data) => {
        console.log('Received price update:', data)
        company.value.current_price = data.price
        company.value.price_change = data.change
      })

      // 订单簿更新
      socket.on('order_book_update', (data) => {
        console.log('Received order book update:', data)
        sellOrders.value = data.sell_orders
        buyOrders.value = data.buy_orders
      })

      // 成交记录更新
      socket.on('trade', (data) => {
        console.log('Received trade:', data)
        recentTrades.value.unshift(data)
        if (recentTrades.value.length > 20) {
          recentTrades.value.pop()
        }
      })

      // 启动连接
      socket.connect()
    }

    // 提交交易
    const submitTrade = async () => {
      try {
        await tradeFormRef.value.validate()
        const companyId = route.query.company
        if (!companyId) {
          ElMessage.error('未指定公司ID')
          return
        }

        loading.value = true
        const response = await fetch('/api/stock/trade', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            company_id: companyId,
            type: tradeForm.type,
            price: tradeForm.price,
            quantity: tradeForm.quantity
          })
        })

        const data = await response.json()
        if (response.ok) {
          ElMessage.success('交易提交成功')
          tradeForm.quantity = 100 // 重置数量
        } else {
          ElMessage.error(data.message || '交易提交失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('交易提交失败:', error)
          ElMessage.error('交易提交失败')
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      const companyId = route.query.company
      if (companyId) {
        fetchCompanyData()
      } else {
        fetchCompanies()
      }
      initSocketListeners()
    })

    onUnmounted(() => {
      // 清理所有监听器
      socket.off('connect')
      socket.off('connect_error')
      socket.off('reconnect')
      socket.off('price_update')
      socket.off('order_book_update')
      socket.off('trade')
      // 断开连接
      socket.disconnect()
    })

    return {
      company,
      tradeForm,
      rules,
      loading,
      tradeFormRef,
      sellOrders,
      buyOrders,
      recentTrades,
      formatNumber,
      formatDate,
      priceChangeClass,
      formatPriceChange,
      calculateFee,
      calculateTotal,
      submitTrade,
      companies,
      selectedCompany,
      selectCompany
    }
  }
}
</script>

<style scoped>
.stock-market {
  padding: 20px;
}

.trade-card {
  margin-bottom: 20px;
}

.company-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-info {
  text-align: right;
}

.current-price {
  font-size: 24px;
  font-weight: bold;
  margin-right: 10px;
}

.price-change {
  font-size: 16px;
}

.price-up {
  color: #67C23A;
}

.price-down {
  color: #F56C6C;
}

.trade-details {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.total {
  font-weight: bold;
  font-size: 16px;
}

.order-book {
  height: 100%;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px;
  margin-bottom: 5px;
}

.sell {
  color: #F56C6C;
}

.buy {
  color: #67C23A;
}
</style> 