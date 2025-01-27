<template>
  <div class="stock-market">
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
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { io } from 'socket.io-client'

export default {
  name: 'StockMarket',
  setup() {
    const route = useRoute()
    const socket = io('/stock')
    const loading = ref(false)
    const tradeFormRef = ref(null)
    
    const company = ref({})
    const sellOrders = ref([])
    const buyOrders = ref([])
    const recentTrades = ref([])

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

    // ... 其他方法实现 ...

    onMounted(() => {
      fetchCompanyData()
      initSocketListeners()
    })

    onUnmounted(() => {
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
      // ... 其他返回值
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