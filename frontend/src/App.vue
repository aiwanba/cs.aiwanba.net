<template>
  <div id="app">
    <h1>股票交易游戏</h1>
    <p>{{ message }}</p>
    <div class="section">
      <h2>公司列表</h2>
      <ul class="list">
        <li v-for="company in companies" :key="company.id" class="list-item" @click="showCompanyDetails(company)">
          <span class="company-name">{{ company.name }}</span>
          <span class="company-balance">余额: {{ company.balance }}</span>
        </li>
      </ul>
    </div>
    <div class="section">
      <h2>交易记录</h2>
      <ul class="list">
        <li v-for="transaction in transactions" :key="transaction.id" class="list-item" @click="showTransactionDetails(transaction)">
          <span class="stock-symbol">{{ transaction.stock_symbol }}</span>
          <span class="quantity">{{ transaction.quantity }} 股</span>
          <span class="price">价格: {{ transaction.price }}</span>
          <span class="transaction-type">类型: {{ transaction.transaction_type }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: "欢迎来到股票交易游戏！",
      companies: [],
      transactions: []
    };
  },
  methods: {
    showCompanyDetails(company) {
      alert(`公司名称: ${company.name}\n余额: ${company.balance}`);
    },
    showTransactionDetails(transaction) {
      alert(`股票代码: ${transaction.stock_symbol}\n数量: ${transaction.quantity}\n价格: ${transaction.price}\n类型: ${transaction.transaction_type}`);
    }
  },
  mounted() {
    // 获取公司列表
    fetch('http://localhost:5010/api/companies')
      .then(response => response.json())
      .then(data => this.companies = data)
      .catch(error => console.error('获取公司列表失败：', error));

    // 获取交易记录
    fetch('http://localhost:5010/api/transactions')
      .then(response => response.json())
      .then(data => this.transactions = data)
      .catch(error => console.error('获取交易记录失败：', error));
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
  cursor: pointer;
}

.list-item:hover {
  background-color: #f1f1f1;
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
</style> 