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
          <!-- 左侧：市场数据和订单簿 -->
          <div class="left-panel">
            <!-- 市场数据表格 -->
            <div class="market-data-table">
              <h3>市场数据</h3>
              <table>
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>开盘价</th>
                    <th>收盘价</th>
                    <th>最高价</th>
                    <th>最低价</th>
                    <th>成交量</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in chartData.kline" :key="item.date">
                    <td>{{ new Date(item.date).toLocaleString() }}</td>
                    <td>{{ item.open }}</td>
                    <td>{{ item.close }}</td>
                    <td>{{ item.high }}</td>
                    <td>{{ item.low }}</td>
                    <td>{{ item.volume }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 订单簿 -->
            <div class="order-book">
              <h3>订单簿</h3>
              <div class="order-lists">
                <!-- 卖单列表 -->
                <div class="sell-orders">
                  <h4>卖单</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>价格</th>
                        <th>数量</th>
                        <th>时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in sellOrders" :key="order.id">
                        <td>{{ order.price }}</td>
                        <td>{{ order.remaining_quantity }}</td>
                        <td>{{ new Date(order.create_time).toLocaleString() }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- 买单列表 -->
                <div class="buy-orders">
                  <h4>买单</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>价格</th>
                        <th>数量</th>
                        <th>时间</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in buyOrders" :key="order.id">
                        <td>{{ order.price }}</td>
                        <td>{{ order.remaining_quantity }}</td>
                        <td>{{ new Date(order.create_time).toLocaleString() }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：交易面板 -->
          <div class="right-panel">
            <!-- 股票信息 -->
            <div v-if="selectedStock" class="stock-info">
              <h3>{{ getCompanyName(selectedStock.company_id) }}</h3>
              <div class="stock-details">
                <div class="detail-item">
                  <span>总股本</span>
                  <span>{{ selectedStock.total_shares }}</span>
                </div>
                <div class="detail-item">
                  <span>流通股</span>
                  <span>{{ selectedStock.circulating_shares }}</span>
                </div>
                <div class="detail-item">
                  <span>发行价</span>
                  <span>{{ selectedStock.issue_price }}</span>
                </div>
              </div>
            </div>

            <!-- 交易表单 -->
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

            <!-- 当前持仓 -->
            <div class="holdings">
              <h3>持仓情况</h3>
              <div v-if="selectedCompanyId" class="holdings-list">
                <div v-for="holding in holdings" :key="holding.target_company_id" class="holding-item">
                  <span>{{ getCompanyName(holding.target_company_id) }}</span>
                  <span>{{ holding.quantity }} 股</span>
                </div>
              </div>
            </div>

            <!-- AI交易状态 -->
            <div v-if="selectedCompany?.is_ai" class="ai-status">
              <h3>AI交易状态</h3>
              <div class="ai-strategy">
                <span>当前策略：{{ currentStrategy?.name }}</span>
                <span>表现：{{ currentStrategy?.performance }}</span>
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
      <div class="section market-section">
        <h2>市场行情</h2>
        
        <!-- 时间范围选择 -->
        <div class="time-range-selector">
          <button 
            v-for="range in ['1d', '1w', '1m', '3m', '6m', '1y']" 
            :key="range"
            :class="['range-btn', { active: selectedTimeRange === range }]"
            @click="changeTimeRange(range)"
          >
            {{ range }}
          </button>
        </div>
        
        <div class="market-charts">
          <!-- 价格走势图 -->
          <div class="chart-container">
            <div ref="priceChart" style="width: 100%; height: 300px;"></div>
          </div>
          
          <!-- 成交量图 -->
          <div class="chart-container">
            <div ref="volumeChart" style="width: 100%; height: 200px;"></div>
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

      <!-- 交易所 -->
      <div v-show="currentTab === 'exchange'" class="section exchange-section">
        <h2>交易所</h2>
        
        <!-- 股票列表 -->
        <div class="stock-list">
          <div class="stock-list-header">
            <div>公司名称</div>
            <div>最新价</div>
            <div>涨跌幅</div>
            <div>成交量</div>
            <div>总市值</div>
            <div>操作</div>
          </div>
          <div v-for="stock in stockList" :key="stock.company_id" class="stock-item">
            <div class="company-name">{{ stock.company_name }}</div>
            <div :class="['price', stock.price_change >= 0 ? 'up' : 'down']">
              {{ stock.current_price }}
            </div>
            <div :class="['change', stock.price_change >= 0 ? 'up' : 'down']">
              {{ (stock.price_change * 100).toFixed(2) }}%
            </div>
            <div>{{ stock.volume }}</div>
            <div>{{ (stock.current_price * stock.total_shares).toFixed(2) }}</div>
            <div class="actions">
              <button @click="openTradeDialog(stock, 'buy')">买入</button>
              <button @click="openTradeDialog(stock, 'sell')">卖出</button>
            </div>
          </div>
        </div>

        <!-- 交易弹窗 -->
        <div v-if="showTradeDialog" class="dialog-overlay" @click.self="closeTradeDialog">
          <div class="trade-dialog">
            <h3>{{ tradeType === 'buy' ? '买入' : '卖出' }}{{ selectedStock?.company_name }}</h3>
            <div class="trade-info">
              <div class="info-item">
                <span>当前价格</span>
                <span>{{ selectedStock?.current_price }}</span>
              </div>
              <div class="info-item">
                <span>可用余额</span>
                <span>{{ selectedCompany?.balance }}</span>
              </div>
              <div class="info-item">
                <span>持有数量</span>
                <span>{{ getCurrentHolding(selectedStock?.company_id) }}</span>
              </div>
            </div>
            <div class="trade-form">
              <div class="form-item">
                <label>价格</label>
                <input v-model.number="tradePrice" type="number" step="0.01" />
              </div>
              <div class="form-item">
                <label>数量</label>
                <input v-model.number="tradeQuantity" type="number" step="100" />
              </div>
              <div class="trade-total">
                总额：{{ (tradePrice * tradeQuantity).toFixed(2) }}
              </div>
            </div>
            <div class="dialog-buttons">
              <button @click="submitTrade">确认</button>
              <button @click="closeTradeDialog">取消</button>
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
      chartData: {
        kline: [], // 市场数据
        depth: { bids: [], asks: [] } // 深度数据
      },
      loading: false,
      error: null,
      successMessage: null,
      currentTab: 'trading',
      tabs: [
        { id: 'company', name: '公司管理' },
        { id: 'exchange', name: '交易所' },
        { id: 'trading', name: '交易中心' }
      ],
      showConfirmDialog: false,
      confirmMessage: '',
      pendingTransaction: null,
      holdings: [],
      buyOrders: [],
      sellOrders: [],
      selectedStock: null,
      currentStrategy: null,
      marketData: {
        prices: [],
        volumes: [],
        timestamps: []
      },
      selectedTimeRange: '1d', // 可选：1d, 1w, 1m, 3m, 6m, 1y
      marketCharts: {
        price: null,
        volume: null
      },
      stockList: [],
      showTradeDialog: false,
      tradeType: 'buy',
      tradePrice: 0,
      tradeQuantity: 0
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
    // 获取市场数据
    async fetchChartData() {
      if (!this.selectedCompanyId) return;

      try {
        this.loading = true;
        // 获取市场数据
        const response = await fetch(
          `http://localhost:5010/api/market/kline/${this.selectedCompanyId}`
        );
        const data = await response.json();
        this.chartData.kline = data;

        // 获取深度数据
        const depthResponse = await fetch(
          `http://localhost:5010/api/market/depth/${this.selectedCompanyId}`
        );
        const depthData = await depthResponse.json();
        this.chartData.depth = depthData;
      } catch (error) {
        console.error('获取市场数据失败：', error);
        this.error = '获取市场数据失败';
      } finally {
        this.loading = false;
      }
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
          await this.fetchChartData();
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
    },
    // 获取订单簿数据
    async fetchOrderBook() {
      if (this.selectedCompanyId) {
        try {
          const response = await fetch(`http://localhost:5010/api/market/orderbook/${this.selectedCompanyId}`);
          const data = await response.json();
          this.buyOrders = data.buy_orders;
          this.sellOrders = data.sell_orders;
        } catch (error) {
          console.error('获取订单簿失败：', error);
        }
      }
    },
    // 获取股票发行信息
    async fetchStockInfo() {
      if (this.selectedCompanyId) {
        try {
          const response = await fetch(`http://localhost:5010/api/stock/info/${this.selectedCompanyId}`);
          const data = await response.json();
          this.selectedStock = data;
        } catch (error) {
          console.error('获取股票信息失败：', error);
        }
      }
    },
    // 获取AI策略信息
    async fetchAIStrategy() {
      if (this.selectedCompanyId) {
        try {
          const response = await fetch(`http://localhost:5010/api/ai/strategy/${this.selectedCompanyId}`);
          const data = await response.json();
          this.currentStrategy = data;
        } catch (error) {
          console.error('获取AI策略失败：', error);
        }
      }
    },
    // 更新深度图数据
    updateDepthChart() {
      if (!this.charts.depth) return;

      const option = {
        title: { text: '市场深度' },
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
          data: [...this.buyOrders, ...this.sellOrders].map(order => order.price)
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: '买单',
          type: 'line',
          data: this.buyOrders.map(order => order.remaining_quantity),
          areaStyle: {},
          itemStyle: { color: '#00da3c' }
        }, {
          name: '卖单',
          type: 'line',
          data: this.sellOrders.map(order => order.remaining_quantity),
          areaStyle: {},
          itemStyle: { color: '#ec0000' }
        }]
      };

      this.charts.depth.setOption(option);
    },
    // 定时更新数据
    startDataUpdates() {
      setInterval(() => {
        this.fetchOrderBook();
        this.fetchChartData();
        if (this.selectedCompany?.is_ai) {
          this.fetchAIStrategy();
        }
      }, 5000);
    },
    // 获取市场行情数据
    async fetchMarketData() {
      if (!this.selectedCompanyId) return;
      
      try {
        this.loading = true;
        const response = await fetch(
          `http://localhost:5010/api/market/data/${this.selectedCompanyId}?range=${this.selectedTimeRange}`
        );
        const data = await response.json();
        
        // 更新市场数据
        this.marketData = {
          prices: data.map(d => ({
            time: new Date(d.date).getTime(),
            value: d.close_price
          })),
          volumes: data.map(d => ({
            time: new Date(d.date).getTime(),
            value: d.volume
          })),
          timestamps: data.map(d => new Date(d.date).getTime())
        };
        
        this.updateMarketCharts();
      } catch (error) {
        console.error('获取市场数据失败：', error);
        this.error = '获取市场数据失败';
      } finally {
        this.loading = false;
      }
    },
    // 初始化市场行情图表
    initMarketCharts() {
      const echarts = require('echarts');
      
      // 初始化价格图表
      this.marketCharts.price = echarts.init(this.$refs.priceChart);
      
      // 初始化成交量图表
      this.marketCharts.volume = echarts.init(this.$refs.volumeChart);
      
      // 添加窗口大小变化监听
      window.addEventListener('resize', () => {
        this.marketCharts.price?.resize();
        this.marketCharts.volume?.resize();
      });
    },
    // 更新市场行情图表
    updateMarketCharts() {
      if (!this.marketCharts.price || !this.marketCharts.volume) return;

      // 价格图表配置
      const priceOption = {
        title: { text: '价格走势' },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const time = new Date(params[0].value[0]).toLocaleString();
            return `${time}<br/>价格：${params[0].value[1]}`;
          }
        },
        xAxis: {
          type: 'time',
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          splitLine: { show: true }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            bottom: 10,
            start: 0,
            end: 100
          }
        ],
        series: [{
          name: '价格',
          type: 'line',
          data: this.marketData.prices.map(p => [p.time, p.value]),
          itemStyle: {
            color: '#3498db'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(52,152,219,0.5)' },
              { offset: 1, color: 'rgba(52,152,219,0.1)' }
            ])
          }
        }]
      };

      // 成交量图表配置
      const volumeOption = {
        title: { text: '成交量' },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const time = new Date(params[0].value[0]).toLocaleString();
            return `${time}<br/>成交量：${params[0].value[1]}`;
          }
        },
        xAxis: {
          type: 'time',
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          splitLine: { show: true }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            bottom: 10,
            start: 0,
            end: 100
          }
        ],
        series: [{
          name: '成交量',
          type: 'bar',
          data: this.marketData.volumes.map(v => [v.time, v.value]),
          itemStyle: {
            color: '#2ecc71'
          }
        }]
      };

      // 更新图表
      try {
        this.marketCharts.price.setOption(priceOption, true);
        this.marketCharts.volume.setOption(volumeOption, true);
      } catch (error) {
        console.error('更新市场行情图表失败：', error);
        this.error = '更新市场行情图表失败';
      }
    },
    // 切换时间范围
    changeTimeRange(range) {
      this.selectedTimeRange = range;
      this.fetchMarketData();
    },
    // 打开交易弹窗
    openTradeDialog(stock, type) {
      this.selectedStock = stock;
      this.tradeType = type;
      this.tradePrice = stock.current_price;
      this.tradeQuantity = 0;
      this.showTradeDialog = true;
    },
    // 关闭交易弹窗
    closeTradeDialog() {
      this.showTradeDialog = false;
      this.selectedStock = null;
      this.tradePrice = 0;
      this.tradeQuantity = 0;
    },
    // 提交交易
    async submitTrade() {
      if (!this.selectedCompanyId || !this.selectedStock) {
        this.error = '请先选择交易公司';
        return;
      }

      try {
        this.loading = true;
        const response = await fetch('http://localhost:5010/api/orders', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            company_id: this.selectedCompanyId,
            target_company_id: this.selectedStock.company_id,
            order_type: this.tradeType,
            price: this.tradePrice,
            quantity: this.tradeQuantity
          })
        });

        const data = await response.json();
        if (response.ok) {
          this.successMessage = '下单成功';
          this.closeTradeDialog();
          this.fetchStockList();
          this.fetchHoldings();
        } else {
          this.error = data.error || '下单失败';
        }
      } catch (error) {
        console.error('交易失败：', error);
        this.error = '交易失败';
      } finally {
        this.loading = false;
      }
    },
    // 获取股票列表
    async fetchStockList() {
      try {
        this.loading = true;
        const response = await fetch('http://localhost:5010/api/exchange/stocks');
        const data = await response.json();
        this.stockList = data;
      } catch (error) {
        console.error('获取股票列表失败：', error);
        this.error = '获取股票列表失败';
      } finally {
        this.loading = false;
      }
    },
    // 获取当前持仓
    getCurrentHolding(companyId) {
      const holding = this.holdings.find(h => h.target_company_id === companyId);
      return holding ? holding.quantity : 0;
    }
  },
  watch: {
    // 监听选中的公司变化
    selectedCompanyId: {
      handler(newVal) {
        if (newVal) {
          this.fetchChartData();
        }
      },
      immediate: true
    },
    // 监听当前标签页变化
    currentTab: {
      handler(newVal) {
        if (newVal === 'trading') {
          this.$nextTick(() => {
            this.fetchChartData();
          });
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.fetchCompanies();
    this.fetchTransactions();
    this.fetchLoans();
    this.fetchCompanyReport();
    this.startDataUpdates();
    this.initMarketCharts();
    this.fetchMarketData();
    this.fetchStockList();

    // 添加窗口大小变化监听
    window.addEventListener('resize', () => {
      this.marketCharts.price?.resize();
      this.marketCharts.volume?.resize();
    });

    // 定时更新股票列表
    setInterval(() => {
      this.fetchStockList();
    }, 5000);
  },
  beforeDestroy() {
    // 清理图表实例和事件监听
    this.marketCharts.price?.dispose();
    this.marketCharts.volume?.dispose();
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

.order-book {
  margin-top: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.order-lists {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.order-header {
  font-weight: bold;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 10px;
  border-bottom: 1px solid #eee;
}

.stock-info {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stock-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 10px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ai-status {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
}

.ai-strategy {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.market-section {
  margin-top: 20px;
}

.time-range-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.range-btn {
  padding: 5px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.range-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.market-charts {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container {
  margin-bottom: 20px;
}

.chart-container:last-child {
  margin-bottom: 0;
}

.exchange-section {
  margin-top: 20px;
}

.stock-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.stock-list-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  padding: 15px;
  background: #f5f5f5;
  font-weight: bold;
}

.stock-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  padding: 15px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.stock-item:last-child {
  border-bottom: none;
}

.price.up, .change.up {
  color: #00C851;
}

.price.down, .change.down {
  color: #ff4444;
}

.actions {
  display: flex;
  gap: 10px;
}

.trade-dialog {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 400px;
}

.trade-info {
  margin: 20px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.trade-form {
  margin: 20px 0;
}

.form-item {
  margin-bottom: 15px;
}

.form-item label {
  display: block;
  margin-bottom: 5px;
}

.trade-total {
  text-align: right;
  font-weight: bold;
  margin-top: 10px;
}

.dialog-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.market-data-table {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: bold;
}

tbody tr:hover {
  background: #f9f9f9;
}

.order-lists {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.sell-orders, .buy-orders {
  background: white;
  padding: 15px;
  border-radius: 8px;
}

.sell-orders h4, .buy-orders h4 {
  margin: 0 0 10px 0;
  color: #333;
}

/* 价格颜色 */
.sell-orders td:first-child {
  color: #ff4444;
}

.buy-orders td:first-child {
  color: #00C851;
}
</style> 