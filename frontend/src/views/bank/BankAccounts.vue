<template>
  <div class="bank-accounts">
    <el-row :gutter="20">
      <!-- 账户概览卡片 -->
      <el-col :span="8">
        <el-card class="account-card">
          <template #header>
            <div class="card-header">
              <span>账户概览</span>
              <el-button type="primary" @click="openAccount" v-if="!hasAccount">
                开立账户
              </el-button>
            </div>
          </template>
          
          <div v-if="hasAccount" class="account-info">
            <div class="info-item">
              <span class="label">账户余额</span>
              <span class="value">¥{{ formatNumber(account.balance) }}</span>
            </div>
            <div class="info-item">
              <span class="label">可用额度</span>
              <span class="value">¥{{ formatNumber(account.available_credit) }}</span>
            </div>
            <div class="info-item">
              <span class="label">贷款余额</span>
              <span class="value">¥{{ formatNumber(account.loan_balance) }}</span>
            </div>
          </div>
          
          <div v-else class="no-account">
            <el-empty description="暂无银行账户" />
          </div>
        </el-card>
      </el-col>

      <!-- 快捷操作卡片 -->
      <el-col :span="16">
        <el-card class="operation-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          
          <el-row :gutter="20" class="operation-buttons">
            <el-col :span="8">
              <el-button type="primary" @click="showDepositDialog">
                <el-icon><plus /></el-icon>
                存款
              </el-button>
            </el-col>
            <el-col :span="8">
              <el-button type="warning" @click="showWithdrawDialog">
                <el-icon><minus /></el-icon>
                取款
              </el-button>
            </el-col>
            <el-col :span="8">
              <el-button type="success" @click="$router.push('/bank/loan')">
                <el-icon><money /></el-icon>
                贷款
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 交易记录卡片 -->
        <el-card class="transaction-card">
          <template #header>
            <div class="card-header">
              <span>最近交易</span>
              <el-button text @click="$router.push('/bank/transactions')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <el-table :data="recentTransactions" stripe>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getTransactionType(row.type)">
                  {{ getTransactionText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">
                <span :class="row.type === 'deposit' ? 'income' : 'expense'">
                  {{ row.type === 'deposit' ? '+' : '-' }}
                  ¥{{ formatNumber(row.amount) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="balance" label="余额">
              <template #default="{ row }">
                ¥{{ formatNumber(row.balance) }}
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 存款对话框 -->
    <el-dialog v-model="depositVisible" title="存款" width="30%">
      <el-form :model="depositForm" :rules="depositRules" ref="depositFormRef">
        <el-form-item label="存款金额" prop="amount">
          <el-input-number v-model="depositForm.amount" :min="100" :step="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="depositVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDeposit" :loading="loading">
          确认存款
        </el-button>
      </template>
    </el-dialog>

    <!-- 取款对话框 -->
    <el-dialog v-model="withdrawVisible" title="取款" width="30%">
      <el-form :model="withdrawForm" :rules="withdrawRules" ref="withdrawFormRef">
        <el-form-item label="取款金额" prop="amount">
          <el-input-number 
            v-model="withdrawForm.amount" 
            :min="100" 
            :max="account.balance" 
            :step="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="withdrawVisible = false">取消</el-button>
        <el-button type="warning" @click="handleWithdraw" :loading="loading">
          确认取款
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Minus, Money } from '@element-plus/icons-vue'

export default {
  name: 'BankAccounts',
  components: {
    Plus,
    Minus,
    Money
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const account = ref({})
    const recentTransactions = ref([])
    const depositVisible = ref(false)
    const withdrawVisible = ref(false)
    const depositFormRef = ref(null)
    const withdrawFormRef = ref(null)

    const depositForm = ref({
      amount: 100
    })

    const withdrawForm = ref({
      amount: 100
    })

    const depositRules = {
      amount: [
        { required: true, message: '请输入存款金额', trigger: 'blur' },
        { type: 'number', min: 100, message: '最小存款金额为100', trigger: 'blur' }
      ]
    }

    const withdrawRules = {
      amount: [
        { required: true, message: '请输入取款金额', trigger: 'blur' },
        { type: 'number', min: 100, message: '最小取款金额为100', trigger: 'blur' }
      ]
    }

    const hasAccount = computed(() => {
      return Object.keys(account.value).length > 0
    })

    const fetchAccountInfo = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/bank/account', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          account.value = data.data || {}
        } else {
          ElMessage.error(data.message || '获取账户信息失败')
        }
      } catch (error) {
        console.error('获取账户信息失败:', error)
        ElMessage.error('获取账户信息失败')
      } finally {
        loading.value = false
      }
    }

    const fetchRecentTransactions = async () => {
      try {
        const response = await fetch('/api/bank/transactions/recent', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const data = await response.json()
        
        if (response.ok) {
          recentTransactions.value = data.data || []
        } else {
          ElMessage.error(data.message || '获取交易记录失败')
        }
      } catch (error) {
        console.error('获取交易记录失败:', error)
        ElMessage.error('获取交易记录失败')
      }
    }

    const openAccount = async () => {
      try {
        // 先获取可用银行列表
        const banksResponse = await fetch('/api/bank/banks', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        const banksData = await banksResponse.json()
        
        if (!banksResponse.ok) {
          throw new Error(banksData.message || '获取银行列表失败')
        }
        
        if (banksData.data.length === 0) {
          ElMessage.warning('暂无可用银行')
          return
        }
        
        // 选择第一个银行开户
        const bankId = banksData.data[0].id
        
        const response = await fetch('/api/bank/account/open', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            bank_id: bankId
          })
        })
        
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.message || '开户失败')
        }
        
        ElMessage.success('开户成功')
        // 刷新账户信息
        fetchAccountInfo()
        
      } catch (error) {
        console.error('开户失败:', error)
        ElMessage.error(error.message || '开户失败')
      }
    }

    const showDepositDialog = () => {
      if (!hasAccount.value) {
        ElMessage.warning('请先开立账户')
        return
      }
      depositVisible.value = true
    }

    const showWithdrawDialog = () => {
      if (!hasAccount.value) {
        ElMessage.warning('请先开立账户')
        return
      }
      withdrawVisible.value = true
    }

    const handleDeposit = async () => {
      try {
        await depositFormRef.value.validate()
        loading.value = true
        
        const response = await fetch('/api/bank/account/deposit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(depositForm.value)
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('存款成功')
          depositVisible.value = false
          fetchAccountInfo()
          fetchRecentTransactions()
        } else {
          ElMessage.error(data.error || '存款失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('存款失败')
        }
      } finally {
        loading.value = false
      }
    }

    const handleWithdraw = async () => {
      try {
        await withdrawFormRef.value.validate()
        loading.value = true
        
        const response = await fetch('/api/bank/account/withdraw', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(withdrawForm.value)
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('取款成功')
          withdrawVisible.value = false
          fetchAccountInfo()
          fetchRecentTransactions()
        } else {
          ElMessage.error(data.error || '取款失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('取款失败')
        }
      } finally {
        loading.value = false
      }
    }

    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN')
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString('zh-CN')
    }

    const getTransactionType = (type) => {
      const types = {
        deposit: 'success',
        withdraw: 'warning',
        loan: 'primary',
        repayment: 'info'
      }
      return types[type] || 'info'
    }

    const getTransactionText = (type) => {
      const texts = {
        deposit: '存款',
        withdraw: '取款',
        loan: '贷款',
        repayment: '还款'
      }
      return texts[type] || type
    }

    onMounted(() => {
      fetchAccountInfo()
      fetchRecentTransactions()
    })

    return {
      account,
      loading,
      hasAccount,
      recentTransactions,
      depositVisible,
      withdrawVisible,
      depositForm,
      withdrawForm,
      depositFormRef,
      withdrawFormRef,
      depositRules,
      withdrawRules,
      openAccount,
      showDepositDialog,
      showWithdrawDialog,
      handleDeposit,
      handleWithdraw,
      formatNumber,
      formatDate,
      getTransactionType,
      getTransactionText
    }
  }
}
</script>

<style scoped>
.bank-accounts {
  padding: 20px;
}

.account-card {
  margin-bottom: 20px;
}

.info-item {
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

.operation-card {
  margin-bottom: 20px;
}

.operation-buttons {
  text-align: center;
}

.income {
  color: #67C23A;
}

.expense {
  color: #F56C6C;
}

.no-account {
  padding: 20px 0;
}
</style> 