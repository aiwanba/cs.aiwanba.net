<template>
  <div id="app">
    <h1>股票交易游戏</h1>
    <p>{{ message }}</p>

    <!-- 公司管理 -->
    <div class="section">
      <h2>公司管理</h2>
      <div>
        <input v-model="newCompanyName" placeholder="公司名称" />
        <input v-model="newCompanyBalance" placeholder="初始余额" type="number" />
        <button @click="createCompany">创建公司</button>
      </div>
      <ul class="list">
        <li v-for="company in companies" :key="company.id" class="list-item">
          <span class="company-name">{{ company.name }}</span>
          <span class="company-balance">余额: {{ company.balance }}</span>
          <button @click="deleteCompany(company.id)">删除</button>
        </li>
      </ul>
    </div>

    <!-- 股票交易 -->
    <div class="section">
      <h2>股票交易</h2>
      <div>
        <select v-model="selectedCompanyId">
          <option v-for="company in companies" :key="company.id" :value="company.id">{{ company.name }}</option>
        </select>
        <input v-model="stockSymbol" placeholder="股票代码" />
        <input v-model="stockQuantity" placeholder="数量" type="number" />
        <input v-model="stockPrice" placeholder="价格" type="number" />
        <button @click="buyStock">买入</button>
        <button @click="sellStock">卖出</button>
      </div>
      <ul class="list">
        <li v-for="transaction in transactions" :key="transaction.id" class="list-item">
          <span class="stock-symbol">{{ transaction.stock_symbol }}</span>
          <span class="quantity">{{ transaction.quantity }} 股</span>
          <span class="price">价格: {{ transaction.price }}</span>
          <span class="transaction-type">类型: {{ transaction.transaction_type }}</span>
        </li>
      </ul>
    </div>

    <!-- 银行操作 -->
    <div class="section">
      <h2>银行操作</h2>
      <div>
        <select v-model="selectedCompanyId">
          <option v-for="company in companies" :key="company.id" :value="company.id">{{ company.name }}</option>
        </select>
        <input v-model="amount" placeholder="金额" type="number" />
        <button @click="deposit">存款</button>
        <button @click="withdraw">取款</button>
      </div>
      <div>
        <select v-model="fromCompanyId">
          <option v-for="company in companies" :key="company.id" :value="company.id">{{ company.name }}</option>
        </select>
        <select v-model="toCompanyId">
          <option v-for="company in companies" :key="company.id" :value="company.id">{{ company.name }}</option>
        </select>
        <input v-model="transferAmount" placeholder="转账金额" type="number" />
        <button @click="transfer">转账</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: "欢迎来到股票交易游戏！",
      companies: [],
      transactions: [],
      newCompanyName: "",
      newCompanyBalance: 0,
      selectedCompanyId: null,
      stockSymbol: "",
      stockQuantity: 0,
      stockPrice: 0,
      amount: 0,
      fromCompanyId: null,
      toCompanyId: null,
      transferAmount: 0
    };
  },
  methods: {
    // 获取公司列表
    fetchCompanies() {
      fetch('http://localhost:5010/api/companies')
        .then(response => response.json())
        .then(data => this.companies = data)
        .catch(error => console.error('获取公司列表失败：', error));
    },
    // 创建公司
    createCompany() {
      fetch('http://localhost:5010/api/companies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.newCompanyName, balance: parseFloat(this.newCompanyBalance) })
      })
        .then(response => response.json())
        .then(data => {
          this.fetchCompanies();
          this.newCompanyName = "";
          this.newCompanyBalance = 0;
        })
        .catch(error => console.error('创建公司失败：', error));
    },
    // 删除公司
    deleteCompany(companyId) {
      fetch(`http://localhost:5010/api/companies/${companyId}`, { method: 'DELETE' })
        .then(response => {
          if (response.ok) this.fetchCompanies();
        })
        .catch(error => console.error('删除公司失败：', error));
    },
    // 获取交易记录
    fetchTransactions() {
      fetch('http://localhost:5010/api/transactions')
        .then(response => response.json())
        .then(data => this.transactions = data)
        .catch(error => console.error('获取交易记录失败：', error));
    },
    // 买入股票
    buyStock() {
      fetch('http://localhost:5010/api/transactions/buy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: this.selectedCompanyId,
          stock_symbol: this.stockSymbol,
          quantity: parseInt(this.stockQuantity),
          price: parseFloat(this.stockPrice)
        })
      })
        .then(response => {
          if (response.ok) this.fetchTransactions();
        })
        .catch(error => console.error('买入股票失败：', error));
    },
    // 卖出股票
    sellStock() {
      fetch('http://localhost:5010/api/transactions/sell', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: this.selectedCompanyId,
          stock_symbol: this.stockSymbol,
          quantity: parseInt(this.stockQuantity),
          price: parseFloat(this.stockPrice)
        })
      })
        .then(response => {
          if (response.ok) this.fetchTransactions();
        })
        .catch(error => console.error('卖出股票失败：', error));
    },
    // 存款
    deposit() {
      fetch('http://localhost:5010/api/bank/deposit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: this.selectedCompanyId, amount: parseFloat(this.amount) })
      })
        .then(response => {
          if (response.ok) this.fetchCompanies();
        })
        .catch(error => console.error('存款失败：', error));
    },
    // 取款
    withdraw() {
      fetch('http://localhost:5010/api/bank/withdraw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: this.selectedCompanyId, amount: parseFloat(this.amount) })
      })
        .then(response => {
          if (response.ok) this.fetchCompanies();
        })
        .catch(error => console.error('取款失败：', error));
    },
    // 转账
    transfer() {
      fetch('http://localhost:5010/api/bank/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_company_id: this.fromCompanyId,
          to_company_id: this.toCompanyId,
          amount: parseFloat(this.transferAmount)
        })
      })
        .then(response => {
          if (response.ok) this.fetchCompanies();
        })
        .catch(error => console.error('转账失败：', error));
    }
  },
  mounted() {
    this.fetchCompanies();
    this.fetchTransactions();
  }
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 50px;
  font-family: Arial, sans-serif;
}

.section {
  margin: 20px auto;
  max-width: 800px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.list {
  list-style-type: none;
  padding: 0;
}

.list-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.list-item:last-child {
  border-bottom: none;
}

.company-name, .stock-symbol {
  font-weight: bold;
}

.company-balance, .quantity, .price, .transaction-type {
  color: #555;
}

button {
  margin-left: 10px;
}
</style> 