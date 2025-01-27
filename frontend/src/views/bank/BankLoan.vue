<template>
  <div class="bank-loan">
    <el-row :gutter="20">
      <!-- 贷款信息卡片 -->
      <el-col :span="8">
        <el-card class="loan-card">
          <template #header>
            <div class="card-header">
              <span>贷款信息</span>
            </div>
          </template>
          
          <div class="loan-info">
            <div class="info-item">
              <span class="label">信用额度</span>
              <span class="value">¥{{ formatNumber(account.credit_limit) }}</span>
            </div>
            <div class="info-item">
              <span class="label">可用额度</span>
              <span class="value">¥{{ formatNumber(account.available_credit) }}</span>
            </div>
            <div class="info-item">
              <span class="label">贷款余额</span>
              <span class="value">¥{{ formatNumber(account.loan_balance) }}</span>
            </div>
            <div class="info-item">
              <span class="label">年化利率</span>
              <span class="value">{{ (account.interest_rate * 100).toFixed(2) }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 贷款操作卡片 -->
      <el-col :span="16">
        <el-card class="operation-card">
          <template #header>
            <div class="card-header">
              <span>贷款操作</span>
            </div>
          </template>
          
          <el-form :model="loanForm" :rules="rules" ref="loanFormRef" label-width="100px">
            <el-form-item label="贷款金额" prop="amount">
              <el-input-number 
                v-model="loanForm.amount"
                :min="1000"
                :max="account.available_credit"
                :step="1000"
                style="width: 200px" />
            </el-form-item>
            
            <el-form-item label="贷款期限" prop="term">
              <el-select v-model="loanForm.term" style="width: 200px">
                <el-option label="7天" value="7" />
                <el-option label="30天" value="30" />
                <el-option label="90天" value="90" />
                <el-option label="180天" value="180" />
                <el-option label="360天" value="360" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleLoan" :loading="loading">
                申请贷款
              </el-button>
            </el-form-item>
          </el-form>

          <div class="loan-details">
            <div class="detail-item">
              <span>贷款金额</span>
              <span>¥{{ formatNumber(loanForm.amount) }}</span>
            </div>
            <div class="detail-item">
              <span>贷款期限</span>
              <span>{{ loanForm.term }}天</span>
            </div>
            <div class="detail-item">
              <span>预计利息</span>
              <span>¥{{ formatNumber(calculateInterest()) }}</span>
            </div>
            <div class="detail-item total">
              <span>到期应还</span>
              <span>¥{{ formatNumber(calculateTotal()) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 贷款记录卡片 -->
        <el-card class="loan-records">
          <template #header>
            <div class="card-header">
              <span>贷款记录</span>
            </div>
          </template>
          
          <el-table :data="loanRecords" stripe>
            <el-table-column prop="created_at" label="贷款时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="贷款金额">
              <template #default="{ row }">
                ¥{{ formatNumber(row.amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="term" label="期限">
              <template #default="{ row }">
                {{ row.term }}天
              </template>
            </el-table-column>
            <el-table-column prop="interest" label="利息">
              <template #default="{ row }">
                ¥{{ formatNumber(row.interest) }}
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="到期日" width="180">
              <template #default="{ row }">
                {{ formatDate(row.due_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getLoanStatusType(row.status)">
                  {{ getLoanStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'BankLoan',
  setup() {
    const loading = ref(false)
    const account = ref({})
    const loanRecords = ref([])
    const loanFormRef = ref(null)

    const loanForm = ref({
      amount: 1000,
      term: '30'
    })

    const rules = {
      amount: [
        { required: true, message: '请输入贷款金额', trigger: 'blur' },
        { type: 'number', min: 1000, message: '最小贷款金额为1000', trigger: 'blur' }
      ],
      term: [
        { required: true, message: '请选择贷款期限', trigger: 'change' }
      ]
    }

    const fetchAccountInfo = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/bank/account')
        const data = await response.json()
        
        if (response.ok) {
          account.value = data.account
        } else {
          ElMessage.error(data.error || '获取账户信息失败')
        }
      } catch (error) {
        ElMessage.error('获取账户信息失败')
      } finally {
        loading.value = false
      }
    }

    const fetchLoanRecords = async () => {
      try {
        const response = await fetch('/api/bank/loans')
        const data = await response.json()
        
        if (response.ok) {
          loanRecords.value = data.loans
        } else {
          ElMessage.error(data.error || '获取贷款记录失败')
        }
      } catch (error) {
        ElMessage.error('获取贷款记录失败')
      }
    }

    const calculateInterest = () => {
      if (!loanForm.value.amount || !loanForm.value.term || !account.value.interest_rate) {
        return 0
      }
      return loanForm.value.amount * account.value.interest_rate * (loanForm.value.term / 360)
    }

    const calculateTotal = () => {
      return loanForm.value.amount + calculateInterest()
    }

    const handleLoan = async () => {
      try {
        await loanFormRef.value.validate()
        
        await ElMessageBox.confirm(
          `确认申请贷款？\n贷款金额：¥${formatNumber(loanForm.value.amount)}\n贷款期限：${loanForm.value.term}天\n预计利息：¥${formatNumber(calculateInterest())}\n到期应还：¥${formatNumber(calculateTotal())}`,
          '确认贷款',
          {
            confirmButtonText: '确认',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        const response = await fetch('/api/bank/loans/apply', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            amount: loanForm.value.amount,
            term: parseInt(loanForm.value.term)
          })
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('贷款申请成功')
          fetchAccountInfo()
          fetchLoanRecords()
        } else {
          ElMessage.error(data.error || '贷款申请失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('贷款申请失败')
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

    const getLoanStatusType = (status) => {
      const types = {
        active: 'warning',
        completed: 'success',
        overdue: 'danger'
      }
      return types[status] || 'info'
    }

    const getLoanStatusText = (status) => {
      const texts = {
        active: '进行中',
        completed: '已还清',
        overdue: '已逾期'
      }
      return texts[status] || status
    }

    onMounted(() => {
      fetchAccountInfo()
      fetchLoanRecords()
    })

    return {
      account,
      loading,
      loanRecords,
      loanForm,
      loanFormRef,
      rules,
      calculateInterest,
      calculateTotal,
      handleLoan,
      formatNumber,
      formatDate,
      getLoanStatusType,
      getLoanStatusText
    }
  }
}
</script>

<style scoped>
.bank-loan {
  padding: 20px;
}

.loan-card, .operation-card {
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

.loan-details {
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
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #EBEEF5;
}
</style> 