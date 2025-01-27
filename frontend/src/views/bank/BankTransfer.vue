<template>
  <div class="bank-transfer">
    <el-row :gutter="20">
      <!-- 账户信息卡片 -->
      <el-col :span="8">
        <el-card class="account-card">
          <template #header>
            <div class="card-header">
              <span>账户信息</span>
            </div>
          </template>
          
          <div class="account-info">
            <div class="info-item">
              <span class="label">账户余额</span>
              <span class="value">¥{{ formatNumber(account.balance) }}</span>
            </div>
            <div class="info-item">
              <span class="label">今日转账限额</span>
              <span class="value">¥{{ formatNumber(account.daily_transfer_limit) }}</span>
            </div>
            <div class="info-item">
              <span class="label">已用额度</span>
              <span class="value">¥{{ formatNumber(account.daily_transferred) }}</span>
            </div>
            <div class="info-item">
              <span class="label">剩余额度</span>
              <span class="value">¥{{ formatNumber(account.daily_transfer_limit - account.daily_transferred) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 转账操作卡片 -->
      <el-col :span="16">
        <el-card class="transfer-card">
          <template #header>
            <div class="card-header">
              <span>转账汇款</span>
            </div>
          </template>
          
          <el-form :model="transferForm" :rules="rules" ref="transferFormRef" label-width="120px">
            <el-form-item label="收款人账号" prop="receiver_account">
              <el-input 
                v-model="transferForm.receiver_account"
                placeholder="请输入收款人账号"
                style="width: 300px" />
            </el-form-item>
            
            <el-form-item label="收款人姓名" prop="receiver_name">
              <el-input 
                v-model="transferForm.receiver_name"
                placeholder="请输入收款人姓名"
                style="width: 300px" />
            </el-form-item>
            
            <el-form-item label="转账金额" prop="amount">
              <el-input-number 
                v-model="transferForm.amount"
                :min="0.01"
                :max="account.balance"
                :precision="2"
                :step="100"
                style="width: 300px" />
            </el-form-item>
            
            <el-form-item label="转账说明" prop="description">
              <el-input 
                v-model="transferForm.description"
                type="textarea"
                placeholder="请输入转账说明"
                :rows="3"
                style="width: 300px" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleTransfer" :loading="loading">
                确认转账
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 转账记录卡片 -->
        <el-card class="transfer-records">
          <template #header>
            <div class="card-header">
              <span>最近转账记录</span>
              <el-button text @click="$router.push('/bank/transactions')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <el-table :data="transferRecords" stripe>
            <el-table-column prop="created_at" label="转账时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'transfer_in' ? 'success' : 'warning'">
                  {{ row.type === 'transfer_in' ? '转入' : '转出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">
                <span :class="row.type === 'transfer_in' ? 'income' : 'expense'">
                  {{ row.type === 'transfer_in' ? '+' : '-' }}
                  ¥{{ formatNumber(row.amount) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="counterparty" label="对方账户" />
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'BankTransfer',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const account = ref({})
    const transferRecords = ref([])
    const transferFormRef = ref(null)

    const transferForm = ref({
      receiver_account: '',
      receiver_name: '',
      amount: 0.01,
      description: ''
    })

    const rules = {
      receiver_account: [
        { required: true, message: '请输入收款人账号', trigger: 'blur' },
        { min: 6, max: 20, message: '账号长度在6-20位之间', trigger: 'blur' }
      ],
      receiver_name: [
        { required: true, message: '请输入收款人姓名', trigger: 'blur' },
        { min: 2, max: 20, message: '姓名长度在2-20位之间', trigger: 'blur' }
      ],
      amount: [
        { required: true, message: '请输入转账金额', trigger: 'blur' },
        { type: 'number', min: 0.01, message: '最小转账金额为0.01', trigger: 'blur' }
      ],
      description: [
        { max: 100, message: '说明最多100个字符', trigger: 'blur' }
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

    const fetchTransferRecords = async () => {
      try {
        const response = await fetch('/api/bank/transfers/recent')
        const data = await response.json()
        
        if (response.ok) {
          transferRecords.value = data.transfers
        } else {
          ElMessage.error(data.error || '获取转账记录失败')
        }
      } catch (error) {
        ElMessage.error('获取转账记录失败')
      }
    }

    const handleTransfer = async () => {
      try {
        await transferFormRef.value.validate()
        
        // 检查转账限额
        const remainingLimit = account.value.daily_transfer_limit - account.value.daily_transferred
        if (transferForm.value.amount > remainingLimit) {
          ElMessage.error(`超出今日转账限额，剩余可用额度：¥${formatNumber(remainingLimit)}`)
          return
        }

        // 检查余额
        if (transferForm.value.amount > account.value.balance) {
          ElMessage.error('账户余额不足')
          return
        }

        await ElMessageBox.confirm(
          `确认转账？\n收款人：${transferForm.value.receiver_name}\n账号：${transferForm.value.receiver_account}\n金额：¥${formatNumber(transferForm.value.amount)}`,
          '确认转账',
          {
            confirmButtonText: '确认',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        loading.value = true
        const response = await fetch('/api/bank/transfer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(transferForm.value)
        })
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('转账成功')
          transferForm.value = {
            receiver_account: '',
            receiver_name: '',
            amount: 0.01,
            description: ''
          }
          fetchAccountInfo()
          fetchTransferRecords()
        } else {
          ElMessage.error(data.error || '转账失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('转账失败')
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

    onMounted(() => {
      fetchAccountInfo()
      fetchTransferRecords()
    })

    return {
      account,
      loading,
      transferRecords,
      transferForm,
      transferFormRef,
      rules,
      handleTransfer,
      formatNumber,
      formatDate
    }
  }
}
</script>

<style scoped>
.bank-transfer {
  padding: 20px;
}

.account-card, .transfer-card {
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

.income {
  color: #67C23A;
}

.expense {
  color: #F56C6C;
}
</style> 