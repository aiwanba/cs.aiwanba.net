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
// ... 脚本部分太长，将在下一条消息中继续
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