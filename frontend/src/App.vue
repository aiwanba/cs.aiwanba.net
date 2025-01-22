<template>
  <div id="app">
    <!-- 加载状态遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button class="close-btn" @click="error = null">×</button>
    </div>

    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
      <button class="close-btn" @click="successMessage = null">×</button>
    </div>

    <h1>股票交易游戏</h1>
    <p>{{ message }}</p>

    <!-- 导航栏 -->
    <nav class="nav-bar">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['nav-btn', { active: currentTab === tab.id }]"
        @click="currentTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </nav>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 公司管理 -->
      <div v-show="currentTab === 'company'" class="section">
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

      <!-- 交易中心 -->
      <div v-show="currentTab === 'trading'" class="section trading-section">
        <div class="trading-layout">
          <!-- 左侧：K线图和深度图 -->
          <div class="chart-container">
            <div class="chart">
              <h3>K线图</h3>
              <div ref="klineChart" style="width: 100%; height: 400px;"></div>
            </div>
            <div class="chart">
              <h3>交易深度</h3>
              <div ref="depthChart" style="width: 100%; height: 400px;"></div>
            </div>
          </div>

          <!-- 右侧：交易操作 -->
          <div class="trading-panel">
            <div class="trading-form">
              <select v-model="selectedCompanyId" @change="handleCompanyChange">
                <option value="">选择交易公司</option>
                <option v-for="company in companies" :key="company.id" :value="company.id">
                  {{ company.name }}
                </option>
              </select>

              <select v-model="targetCompanyId" @change="handleTargetChange">
                <option value="">选择目标股票</option>
                <option v-for="company in companies" :key="company.id" :value="company.id">
                  {{ company.name }}的股票
                </option>
              </select>

              <div class="price-input">
                <label>价格</label>
                <div class="price-controls">
                  <button @click="adjustPrice(-0.1)">-</button>
                  <input v-model="stockPrice" type="number" step="0.1" />
                  <button @click="adjustPrice(0.1)">+</button>
                </div>
              </div>

              <div class="quantity-input">
                <label>数量</label>
                <div class="quantity-controls">
                  <button @click="adjustQuantity(-100)">-</button>
                  <input v-model="stockQuantity" type="number" step="100" />
                  <button @click="adjustQuantity(100)">+</button>
                </div>
              </div>

              <div class="trading-buttons">
                <button class="buy-btn" @click="confirmTrade('buy')">买入</button>
                <button class="sell-btn" @click="confirmTrade('sell')">卖出</button>
              </div>
            </div>

            <div class="holdings-panel">
              <h3>持仓情况</h3>
              <div v-if="selectedCompanyId" class="holdings-list">
                <div v-for="holding in holdings" :key="holding.target_company_id" class="holding-item">
                  <span>{{ getCompanyName(holding.target_company_id) }}</span>
                  <span>{{ holding.quantity }} 股</span>
                </div>
              </div>
            </div>
          </div>
        </div>
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

      <!-- 市场行情 -->
      <div class="section">
        <h2>市场行情</h2>
        <div class="market-data">
          <div class="chart">
            <h3>K线图</h3>
            <!-- 使用 ECharts 绘制 K 线图 -->
            <div ref="klineChart" style="width: 100%; height: 400px;"></div>
          </div>
          <div class="chart">
            <h3>交易深度</h3>
            <!-- 使用 ECharts 绘制深度图 -->
            <div ref="depthChart" style="width: 100%; height: 400px;"></div>
          </div>
        </div>
      </div>

      <!-- 贷款系统 -->
      <div class="section">
        <h2>贷款系统</h2>
        <div>
          <select v-model="selectedCompanyId">
            <option v-for="company in companies" :key="company.id" :value="company.id">
              {{ company.name }}
            </option>
          </select>
          <input v-model="loanAmount" type="number" placeholder="贷款金额" />
          <input v-model="loanDuration" type="number" placeholder="贷款期限(月)" />
          <button @click="applyLoan">申请贷款</button>
        </div>
        <div class="loan-list">
          <h3>当前贷款</h3>
          <ul class="list">
            <li v-for="loan in loans" :key="loan.id" class="list-item">
              <span>金额: {{ loan.amount }}</span>
              <span>利率: {{ loan.interest_rate }}%</span>
              <span>状态: {{ loan.status }}</span>
              <button v-if="loan.status === 'active'" @click="repayLoan(loan.id)">
                还款
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- 公司业绩 -->
      <div class="section">
        <h2>公司业绩</h2>
        <div class="company-performance">
          <select v-model="selectedCompanyId">
            <option v-for="company in companies" :key="company.id" :value="company.id">
              {{ company.name }}
            </option>
          </select>
          <div class="chart">
            <h3>业绩走势</h3>
            <!-- 使用 ECharts 绘制业绩图表 -->
            <div ref="performanceChart" style="width: 100%; height: 400px;"></div>
          </div>
          <div class="financial-metrics">
            <div class="metric">
              <h4>营收</h4>
              <p>{{ selectedCompanyReport.revenue }}</p>
            </div>
            <div class="metric">
              <h4>利润</h4>
              <p>{{ selectedCompanyReport.profit }}</p>
            </div>
            <div class="metric">
              <h4>资产</h4>
              <p>{{ selectedCompanyReport.assets }}</p>
            </div>
            <div class="metric">
              <h4>负债</h4>
              <p>{{ selectedCompanyReport.liabilities }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="dialog-overlay">
      <div class="dialog">
        <h3>确认交易</h3>
        <p>
          {{ confirmMessage }}
        </p>
        <div class="dialog-buttons">
          <button @click="executeTransaction">确认</button>
          <button @click="showConfirmDialog = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  data() {
    return {
      message: "欢迎来到股票交易游戏！",
      companies: [],
      transactions: [],
      newCompanyName: "",
      newCompanyBalance: 0,
      selectedCompanyId: null,
      targetCompanyId: null,
      stockQuantity: 0,
      stockPrice: 0,
      amount: 0,
      fromCompanyId: null,
      toCompanyId: null,
      transferAmount: 0,
      loans: [],
      loanAmount: 0,
      loanDuration: 12,
      selectedCompanyReport: {
        revenue: 0,
        profit: 0,
        assets: 0,
        liabilities: 0
      },
      klineChart: null,
      depthChart: null,
      performanceChart: null,
      klineData: [],
      depthData: { bids: [], asks: [] },
      loading: false,
      error: null,
      successMessage: null,
      currentTab: 'trading',
      tabs: [
        { id: 'trading', name: '交易中心' },
        { id: 'company', name: '公司管理' },
        { id: 'bank', name: '银行业务' },
        { id: 'report', name: '业绩报表' }
      ],
      showConfirmDialog: false,
      confirmMessage: '',
      pendingTransaction: null,
      holdings: []
    };
  },
  methods: {
    // 获取公司名称
    getCompanyName(companyId) {
      const company = this.companies.find(c => c.id === companyId);
      return company ? company.name : '未知公司';
    },
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
          target_company_id: this.targetCompanyId,
          quantity: parseInt(this.stockQuantity),
          price: parseFloat(this.stockPrice)
        })
      })
        .then(response => {
          if (response.ok) {
            this.fetchTransactions();
            this.fetchCompanies();
          }
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
          target_company_id: this.targetCompanyId,
          quantity: parseInt(this.stockQuantity),
          price: parseFloat(this.stockPrice)
        })
      })
        .then(response => {
          if (response.ok) {
            this.fetchTransactions();
            this.fetchCompanies();
          }
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
    },
    // 初始化图表
    initCharts() {
      this.klineChart = echarts.init(this.$refs.klineChart);
      this.depthChart = echarts.init(this.$refs.depthChart);
      this.performanceChart = echarts.init(this.$refs.performanceChart);
      this.updateCharts();
    },
    // 更新图表数据
    updateCharts() {
      // K线图配置
      const klineOption = {
        title: { text: '股票K线图' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: { data: ['K线', 'MA5', 'MA10'] },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: this.klineData.map(item => item.date),
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          splitNumber: 20
        },
        yAxis: {
          type: 'value',
          scale: true,
          splitLine: { show: true }
        },
        series: [{
          name: 'K线',
          type: 'candlestick',
          data: this.klineData.map(item => [
            item.open,
            item.close,
            item.low,
            item.high
          ])
        }]
      };
      this.klineChart.setOption(klineOption);

      // 深度图配置
      const depthOption = {
        title: { text: '交易深度图' },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: {
          data: ['买单', '卖单']
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          scale: true,
          splitLine: { show: true }
        },
        series: [{
          name: '买单',
          type: 'line',
          data: this.depthData.bids,
          areaStyle: {},
          lineStyle: {
            color: '#00da3c'
          },
          itemStyle: {
            color: '#00da3c'
          }
        }, {
          name: '卖单',
          type: 'line',
          data: this.depthData.asks,
          areaStyle: {},
          lineStyle: {
            color: '#ec0000'
          },
          itemStyle: {
            color: '#ec0000'
          }
        }]
      };
      this.depthChart.setOption(depthOption);
    },
    // 获取K线数据
    async fetchKlineData() {
      if (this.selectedCompanyId) {
        try {
          const response = await fetch(`http://localhost:5010/api/market/kline/${this.selectedCompanyId}`);
          const data = await response.json();
          this.klineData = data;
          this.updateCharts();
        } catch (error) {
          console.error('获取K线数据失败：', error);
        }
      }
    },
    // 定时更新图表数据
    startChartUpdates() {
      setInterval(() => {
        this.fetchKlineData();
      }, 5000); // 每5秒更新一次
    },
    // 贷款相关方法
    applyLoan() {
      fetch('http://localhost:5010/api/bank/loan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: this.selectedCompanyId,
          amount: this.loanAmount,
          duration: this.loanDuration
        })
      })
        .then(response => response.json())
        .then(data => {
          this.fetchLoans();
          this.fetchCompanies();
        })
        .catch(error => console.error('申请贷款失败：', error));
    },
    repayLoan(loanId) {
      fetch(`http://localhost:5010/api/bank/loan/${loanId}/repay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => response.json())
        .then(data => {
          this.fetchLoans();
          this.fetchCompanies();
        })
        .catch(error => console.error('还款失败：', error));
    },
    // 获取贷款列表
    fetchLoans() {
      fetch('http://localhost:5010/api/bank/loans')
        .then(response => response.json())
        .then(data => this.loans = data)
        .catch(error => console.error('获取贷款列表失败：', error));
    },
    // 获取公司业绩报表
    fetchCompanyReport() {
      if (this.selectedCompanyId) {
        fetch(`http://localhost:5010/api/companies/${this.selectedCompanyId}/report`)
          .then(response => response.json())
          .then(data => this.selectedCompanyReport = data)
          .catch(error => console.error('获取公司业绩报表失败：', error));
      }
    },
    async handleCompanyChange() {
      if (this.selectedCompanyId) {
        this.loading = true;
        try {
          await this.fetchHoldings();
          await this.fetchKlineData();
        } catch (error) {
          this.error = '数据加载失败';
        } finally {
          this.loading = false;
        }
      }
    },
    async fetchHoldings() {
      try {
        const response = await fetch(`http://localhost:5010/api/holdings/${this.selectedCompanyId}`);
        const data = await response.json();
        this.holdings = data;
      } catch (error) {
        console.error('获取持仓数据失败：', error);
        throw error;
      }
    },
    adjustPrice(delta) {
      this.stockPrice = Math.max(0, parseFloat(this.stockPrice || 0) + delta);
    },
    adjustQuantity(delta) {
      this.stockQuantity = Math.max(0, parseInt(this.stockQuantity || 0) + delta);
    },
    confirmTrade(type) {
      if (!this.selectedCompanyId || !this.targetCompanyId) {
        this.error = '请选择交易公司和目标股票';
        return;
      }

      if (!this.stockPrice || !this.stockQuantity) {
        this.error = '请输入有效的价格和数量';
        return;
      }

      this.pendingTransaction = {
        type,
        company_id: this.selectedCompanyId,
        target_company_id: this.targetCompanyId,
        price: this.stockPrice,
        quantity: this.stockQuantity
      };

      this.confirmMessage = `确认${type === 'buy' ? '买入' : '卖出'} ${this.getCompanyName(this.targetCompanyId)}的股票
        数量：${this.stockQuantity}
        价格：${this.stockPrice}
        总额：${this.stockQuantity * this.stockPrice}`;

      this.showConfirmDialog = true;
    },
    async executeTransaction() {
      this.loading = true;
      try {
        const response = await fetch(`http://localhost:5010/api/transactions/${this.pendingTransaction.type}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.pendingTransaction)
        });

        const data = await response.json();
        if (response.ok) {
          this.successMessage = `交易成功！`;
          await this.fetchHoldings();
          await this.fetchTransactions();
          await this.fetchCompanies();
        } else {
          this.error = data.error || '交易失败';
        }
      } catch (error) {
        this.error = '交易执行失败';
      } finally {
        this.loading = false;
        this.showConfirmDialog = false;
      }
    }
  },
  mounted() {
    this.fetchCompanies();
    this.fetchTransactions();
    this.initCharts();
    this.fetchLoans();
    this.fetchCompanyReport();
    this.startChartUpdates();

    // 添加窗口大小变化监听
    window.addEventListener('resize', () => {
      this.klineChart?.resize();
      this.depthChart?.resize();
      this.performanceChart?.resize();
    });
  },
  beforeDestroy() {
    // 清理图表实例
    this.klineChart?.dispose();
    this.depthChart?.dispose();
    this.performanceChart?.dispose();
    window.removeEventListener('resize');
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

select, input {
  margin: 5px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.market-data {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.chart {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.financial-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-top: 20px;
}

.metric {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.metric h4 {
  margin: 0;
  color: #666;
}

.metric p {
  margin: 10px 0 0;
  font-size: 1.2em;
  font-weight: bold;
}

.loan-list {
  margin-top: 20px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message, .success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px;
  border-radius: 4px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.error-message {
  background: #ff4444;
  color: white;
}

.success-message {
  background: #00C851;
  color: white;
}

.nav-bar {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  gap: 10px;
}

.nav-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background: #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-btn.active {
  background: #3498db;
  color: white;
}

.trading-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.trading-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.price-controls, .quantity-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trading-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.buy-btn, .sell-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.buy-btn {
  background: #00C851;
}

.sell-btn {
  background: #ff4444;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 300px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style> 