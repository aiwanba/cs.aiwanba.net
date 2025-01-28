<template>
  <div class="company-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>公司详情</span>
          <div class="header-actions">
            <el-button type="success" @click="goToTrade">交易</el-button>
            <el-button @click="$router.push('/company/list')">返回列表</el-button>
          </div>
        </div>
      </template>

      <div v-if="company">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="公司名称">{{ company.name }}</el-descriptions-item>
          <el-descriptions-item label="所属行业">{{ company.industry }}</el-descriptions-item>
          <el-descriptions-item label="总股本">{{ formatNumber(company.total_shares || 0) }}</el-descriptions-item>
          <el-descriptions-item label="当前股价">¥{{ formatNumber(company.current_price || 0) }}</el-descriptions-item>
          <el-descriptions-item label="市值">¥{{ formatNumber((company.total_shares * company.current_price) || 0) }}</el-descriptions-item>
          <el-descriptions-item label="现金余额">¥{{ formatNumber(company.cash_balance || 0) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(company.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 股价走势图 -->
        <div class="price-chart">
          <div class="chart-header">
            <h3>股价走势</h3>
            <el-radio-group v-model="timeRange" size="small" @change="updateChart">
              <el-radio-button label="day">日</el-radio-button>
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="month">月</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="chartRef" class="chart-container"></div>
        </div>

        <!-- 股东列表 -->
        <div v-if="shareholders.length" class="shareholders">
          <h3>股东列表</h3>
          <el-table :data="shareholders" stripe>
            <el-table-column prop="username" label="股东名称" />
            <el-table-column prop="shares" label="持股数量">
              <template #default="{ row }">
                {{ formatNumber(row.shares) }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="持股比例">
              <template #default="{ row }">
                {{ row.percentage.toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import companyService from '@/services/company'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const company = ref(null)
const shareholders = ref([])
const timeRange = ref('day')
const chartRef = ref(null)
let chart = null

const fetchCompanyDetail = async () => {
  try {
    loading.value = true
    const response = await companyService.getCompanyDetail(route.params.id)
    if (response.data) {
      company.value = response.data
      shareholders.value = response.data.shareholders || []
      initChart()
    }
  } catch (error) {
    console.error('获取公司详情失败:', error)
    ElMessage.error('获取公司详情失败')
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = async () => {
  try {
    const response = await fetch(`/api/company/${route.params.id}/price-history?range=${timeRange.value}`)
    const data = await response.json()
    
    if (response.ok) {
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.times
        },
        yAxis: {
          type: 'value',
          name: '股价'
        },
        series: [{
          data: data.prices,
          type: 'line',
          smooth: true
        }]
      }
      
      chart.setOption(option)
    }
  } catch (error) {
    ElMessage.error('获取股价历史数据失败')
  }
}

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  return Number(num).toLocaleString('zh-CN')
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const goToTrade = () => {
  router.push(`/stock/market?company=${route.params.id}`)
}

onMounted(() => {
  fetchCompanyDetail()
  window.addEventListener('resize', () => {
    chart && chart.resize()
  })
})

onUnmounted(() => {
  chart && chart.dispose()
})
</script>

<style scoped>
.company-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-chart {
  margin-top: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-container {
  height: 400px;
}

.shareholders {
  margin-top: 20px;
}

h3 {
  margin-bottom: 20px;
}
</style> 