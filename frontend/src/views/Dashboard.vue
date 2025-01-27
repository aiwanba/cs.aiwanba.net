<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 个人资产卡片 -->
      <el-col :span="8">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>个人资产</span>
            </div>
          </template>
          <div class="data-content">
            <div class="data-item">
              <span class="label">现金余额</span>
              <span class="value">¥{{ formatNumber(userAssets.cash) }}</span>
            </div>
            <div class="data-item">
              <span class="label">股票市值</span>
              <span class="value">¥{{ formatNumber(userAssets.stockValue) }}</span>
            </div>
            <div class="data-item">
              <span class="label">总资产</span>
              <span class="value highlight">¥{{ formatNumber(userAssets.total) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 持仓概览卡片 -->
      <el-col :span="8">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>持仓概览</span>
            </div>
          </template>
          <div class="data-content">
            <div class="data-item">
              <span class="label">持仓公司数</span>
              <span class="value">{{ stockSummary.companyCount }}</span>
            </div>
            <div class="data-item">
              <span class="label">持仓股数</span>
              <span class="value">{{ formatNumber(stockSummary.totalShares) }}</span>
            </div>
            <div class="data-item">
              <span class="label">浮动盈亏</span>
              <span class="value" :class="stockSummary.profit >= 0 ? 'profit' : 'loss'">
                ¥{{ formatNumber(stockSummary.profit) }}
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 银行账户卡片 -->
      <el-col :span="8">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>银行账户</span>
            </div>
          </template>
          <div class="data-content">
            <div class="data-item">
              <span class="label">存款总额</span>
              <span class="value">¥{{ formatNumber(bankSummary.savings) }}</span>
            </div>
            <div class="data-item">
              <span class="label">贷款总额</span>
              <span class="value">¥{{ formatNumber(bankSummary.loans) }}</span>
            </div>
            <div class="data-item">
              <span class="label">净资产</span>
              <span class="value">¥{{ formatNumber(bankSummary.netAssets) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 市场行情图表 -->
    <el-card class="market-chart">
      <template #header>
        <div class="card-header">
          <span>市场行情</span>
          <el-radio-group v-model="chartTimeRange" size="small">
            <el-radio-button label="day">日</el-radio-button>
            <el-radio-button label="week">周</el-radio-button>
            <el-radio-button label="month">月</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import http from '../services/http'

const store = useStore()
const chartRef = ref(null)
const chartTimeRange = ref('day')
let chart = null

const userAssets = ref({
  cash: 0,
  stockValue: 0,
  total: 0
})

const stockSummary = ref({
  companyCount: 0,
  totalShares: 0,
  profit: 0
})

const bankSummary = ref({
  savings: 0,
  loans: 0,
  netAssets: 0
})

const fetchDashboardData = async () => {
  try {
    const data = await http.get('/api/dashboard/summary')
    userAssets.value = data.userAssets
    stockSummary.value = data.stockSummary
    bankSummary.value = data.bankSummary
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
}

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['市场指数', '交易量']
    },
    xAxis: {
      type: 'category',
      data: ['9:30', '10:30', '11:30', '13:30', '14:30', '15:00']
    },
    yAxis: [
      {
        type: 'value',
        name: '指数'
      },
      {
        type: 'value',
        name: '成交量'
      }
    ],
    series: [
      {
        name: '市场指数',
        type: 'line',
        data: [1000, 1050, 1030, 1080, 1100, 1090]
      },
      {
        name: '交易量',
        type: 'bar',
        yAxisIndex: 1,
        data: [2000, 2500, 1800, 3000, 2800, 2600]
      }
    ]
  }
  
  chart.setOption(option)
}

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDashboardData()
  initChart()
  window.addEventListener('resize', () => {
    chart && chart.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-content {
  padding: 10px 0;
}

.data-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.label {
  color: #666;
}

.value {
  font-weight: bold;
}

.highlight {
  color: #409EFF;
  font-size: 18px;
}

.profit {
  color: #67C23A;
}

.loss {
  color: #F56C6C;
}

.market-chart {
  margin-top: 20px;
}

.chart-container {
  height: 400px;
}
</style> 