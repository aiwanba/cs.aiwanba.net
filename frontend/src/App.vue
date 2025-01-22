<template>
  <div id="app">
    <!-- 加载状态 -->
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

    <!-- 导航栏 -->
    <nav class="nav-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-btn', { active: currentTab === tab.id }]"
        @click="currentTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </nav>

    <!-- 公司管理 -->
    <div v-show="currentTab === 'company'" class="section">
      <h2>公司管理</h2>
      <!-- 公司列表 -->
      <table>
        <thead>
          <tr>
            <th>公司名称</th>
            <th>余额</th>
            <th>类型</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in companies" :key="company.id">
            <td>{{ company.name }}</td>
            <td>{{ company.balance }}</td>
            <td>{{ company.is_ai ? 'AI公司' : '玩家公司' }}</td>
            <td>
              <button @click="selectCompany(company)">选择</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 创建公司表单 -->
      <div class="create-company">
        <h3>创建新公司</h3>
        <div class="form-group">
          <label>公司名称</label>
          <input v-model="newCompany.name" type="text">
        </div>
        <div class="form-group">
          <label>初始资金</label>
          <input v-model.number="newCompany.balance" type="number">
        </div>
        <div class="form-group">
          <label>公司类型</label>
          <select v-model="newCompany.is_ai">
            <option :value="false">玩家公司</option>
            <option :value="true">AI公司</option>
          </select>
        </div>
        <button @click="createCompany">创建公司</button>
      </div>
    </div>

    <!-- 交易所 -->
    <div v-show="currentTab === 'exchange'" class="section">
      <h2>交易所</h2>
      
      <!-- 股票发行 -->
      <div v-if="selectedCompany" class="stock-issue">
        <h3>股票发行</h3>
        <div class="form-group">
          <label>发行总量</label>
          <input v-model.number="issueForm.total_shares" type="number" min="1000">
        </div>
        <div class="form-group">
          <label>流通股数</label>
          <input v-model.number="issueForm.circulating_shares" type="number" min="1000">
        </div>
        <div class="form-group">
          <label>发行价格</label>
          <input v-model.number="issueForm.issue_price" type="number" step="0.01" min="0.01">
        </div>
        <button @click="issueStock" class="issue-btn">发行股票</button>
      </div>

      <!-- 市场概览 -->
      <div class="market-overview">
        <div class="stat-card">
          <h4>总市值</h4>
          <p>{{ totalMarketValue.toFixed(2) }}</p>
        </div>
        <div class="stat-card">
          <h4>今日成交额</h4>
          <p>{{ todayVolume.toFixed(2) }}</p>
        </div>
        <div class="stat-card">
          <h4>上市公司数</h4>
          <p>{{ listedCompanies }}</p>
        </div>
      </div>

      <!-- 股票列表 -->
      <div class="stock-list">
        <table>
          <thead>
            <tr>
              <th>代码</th>
              <th>公司名称</th>
              <th>最新价</th>
              <th>涨跌幅</th>
              <th>开盘价</th>
              <th>最高价</th>
              <th>最低价</th>
              <th>成交量</th>
              <th>成交额</th>
              <th>总市值</th>
              <th>流通市值</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in stocks" :key="stock.company_id">
              <td>{{ stock.company_id.toString().padStart(6, '0') }}</td>
              <td>{{ stock.company_name }}</td>
              <td>{{ stock.current_price }}</td>
              <td :class="stock.price_change >= 0 ? 'up' : 'down'">
                {{ (stock.price_change * 100).toFixed(2) }}%
              </td>
              <td>{{ stock.open_price }}</td>
              <td>{{ stock.high_price }}</td>
              <td>{{ stock.low_price }}</td>
              <td>{{ stock.volume }}</td>
              <td>{{ (stock.volume * stock.current_price).toFixed(2) }}</td>
              <td>{{ (stock.current_price * stock.total_shares).toFixed(2) }}</td>
              <td>{{ (stock.current_price * stock.circulating_shares).toFixed(2) }}</td>
              <td class="actions">
                <button @click="openTradeDialog(stock, 'buy')" class="buy-btn">买入</button>
                <button @click="openTradeDialog(stock, 'sell')" class="sell-btn">卖出</button>
                <button @click="viewStockDetail(stock)" class="detail-btn">详情</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 我的订单 -->
      <div v-if="selectedCompany" class="my-orders">
        <h3>我的订单</h3>
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>股票</th>
              <th>类型</th>
              <th>价格</th>
              <th>数量</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in myOrders" :key="order.id">
              <td>{{ new Date(order.create_time).toLocaleString() }}</td>
              <td>{{ getCompanyName(order.target_company_id) }}</td>
              <td :class="order.order_type">{{ order.order_type === 'buy' ? '买入' : '卖出' }}</td>
              <td>{{ order.price }}</td>
              <td>{{ order.remaining_quantity }}/{{ order.quantity }}</td>
              <td>{{ getOrderStatus(order.status) }}</td>
              <td>
                <button 
                  v-if="order.status === 'pending' || order.status === 'partial'"
                  @click="cancelOrder(order.id)" 
                  class="cancel-btn"
                >
                  撤单
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 交易历史 -->
      <div v-if="selectedCompany" class="trade-history">
        <h3>交易历史</h3>
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>股票</th>
              <th>类型</th>
              <th>价格</th>
              <th>数量</th>
              <th>成交额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in tradeHistory" :key="trade.id">
              <td>{{ new Date(trade.transaction_date).toLocaleString() }}</td>
              <td>{{ getCompanyName(trade.target_company_id) }}</td>
              <td :class="trade.transaction_type">
                {{ trade.transaction_type === 'buy' ? '买入' : '卖出' }}
              </td>
              <td>{{ trade.price }}</td>
              <td>{{ trade.quantity }}</td>
              <td>{{ (trade.price * trade.quantity).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 交易中心 -->
    <div v-show="currentTab === 'trading'" class="section">
      <h2>交易中心</h2>
      <div class="trading-layout">
        <!-- 左侧：市场数据和订单簿 -->
        <div class="left-panel">
          <!-- 市场数据 -->
          <div class="market-data">
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
                <tr v-for="data in marketData" :key="data.date">
                  <td>{{ new Date(data.date).toLocaleString() }}</td>
                  <td>{{ data.open_price }}</td>
                  <td>{{ data.close_price }}</td>
                  <td>{{ data.high_price }}</td>
                  <td>{{ data.low_price }}</td>
                  <td>{{ data.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 订单簿 -->
          <div class="order-book">
            <h3>订单簿</h3>
            <div class="order-lists">
              <!-- 卖单 -->
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

              <!-- 买单 -->
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
          <!-- 当前选中的公司 -->
          <div v-if="selectedCompany" class="company-info">
            <h3>当前公司：{{ selectedCompany.name }}</h3>
            <p>可用资金：{{ selectedCompany.balance }}</p>
          </div>

          <!-- 持仓信息 -->
          <div class="holdings">
            <h3>持仓信息</h3>
            <table>
              <thead>
                <tr>
                  <th>股票名称</th>
                  <th>持有数量</th>
                  <th>当前价值</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="holding in holdings" :key="holding.id">
                  <td>{{ getCompanyName(holding.target_company_id) }}</td>
                  <td>{{ holding.quantity }}</td>
                  <td>{{ (holding.quantity * getStockPrice(holding.target_company_id)).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
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
            <input v-model.number="tradePrice" type="number" step="0.01">
          </div>
          <div class="form-item">
            <label>数量</label>
            <input v-model.number="tradeQuantity" type="number" step="100">
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
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      loading: false,
      error: null,
      successMessage: null,
      currentTab: 'company',
      tabs: [
        { id: 'company', name: '公司管理' },
        { id: 'exchange', name: '交易所' },
        { id: 'trading', name: '交易中心' }
      ],
      companies: [],
      stocks: [],
      marketData: [],
      holdings: [],
      buyOrders: [],
      sellOrders: [],
      selectedCompany: null,
      selectedStock: null,
      showTradeDialog: false,
      tradeType: 'buy',
      tradePrice: 0,
      tradeQuantity: 0,
      newCompany: {
        name: '',
        balance: 1000000,
        is_ai: false
      },
      issueForm: {
        total_shares: 10000,
        circulating_shares: 5000,
        issue_price: 1.00
      },
      totalMarketValue: 0,
      todayVolume: 0,
      listedCompanies: 0,
      myOrders: [],
      tradeHistory: []
    }
  },
  methods: {
    // 获取公司列表
    async fetchCompanies() {
      try {
        const response = await fetch('http://localhost:5010/api/companies');
        this.companies = await response.json();
      } catch (error) {
        this.error = '获取公司列表失败';
        console.error(error);
      }
    },

    // 获取股票列表
    async fetchStocks() {
      try {
        const response = await fetch('http://localhost:5010/api/exchange/stocks');
        this.stocks = await response.json();
      } catch (error) {
        this.error = '获取股票列表失败';
        console.error(error);
      }
    },

    // 获取市场数据
    async fetchMarketData() {
      if (!this.selectedCompany) return;
      try {
        const response = await fetch(`http://localhost:5010/api/market/data/${this.selectedCompany.id}`);
        this.marketData = await response.json();
      } catch (error) {
        this.error = '获取市场数据失败';
        console.error(error);
      }
    },

    // 获取持仓信息
    async fetchHoldings() {
      if (!this.selectedCompany) return;
      try {
        const response = await fetch(`http://localhost:5010/api/holdings/${this.selectedCompany.id}`);
        this.holdings = await response.json();
      } catch (error) {
        this.error = '获取持仓信息失败';
        console.error(error);
      }
    },

    // 获取订单簿
    async fetchOrderBook() {
      if (!this.selectedCompany) return;
      try {
        const response = await fetch(`http://localhost:5010/api/market/orderbook/${this.selectedCompany.id}`);
        const data = await response.json();
        this.buyOrders = data.buy_orders;
        this.sellOrders = data.sell_orders;
      } catch (error) {
        this.error = '获取订单簿失败';
        console.error(error);
      }
    },

    // 创建公司
    async createCompany() {
      try {
        const response = await fetch('http://localhost:5010/api/companies', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newCompany)
        });
        const data = await response.json();
        if (response.ok) {
          this.successMessage = '创建公司成功';
          this.fetchCompanies();
          this.newCompany = { name: '', balance: 1000000, is_ai: false };
        } else {
          this.error = data.error || '创建公司失败';
        }
      } catch (error) {
        this.error = '创建公司失败';
        console.error(error);
      }
    },

    // 选择公司
    selectCompany(company) {
      this.selectedCompany = company;
      this.fetchHoldings();
      this.fetchMarketData();
      this.fetchOrderBook();
    },

    // 打开交易弹窗
    openTradeDialog(stock, type) {
      if (!this.selectedCompany) {
        this.error = '请先选择公司';
        return;
      }
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
      try {
        const response = await fetch('http://localhost:5010/api/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            company_id: this.selectedCompany.id,
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
          this.fetchHoldings();
          this.fetchOrderBook();
        } else {
          this.error = data.error || '下单失败';
        }
      } catch (error) {
        this.error = '下单失败';
        console.error(error);
      }
    },

    // 获取公司名称
    getCompanyName(id) {
      const company = this.companies.find(c => c.id === id);
      return company ? company.name : '未知公司';
    },

    // 获取股票价格
    getStockPrice(id) {
      const stock = this.stocks.find(s => s.company_id === id);
      return stock ? stock.current_price : 0;
    },

    // 获取当前持仓
    getCurrentHolding(companyId) {
      const holding = this.holdings.find(h => h.target_company_id === companyId);
      return holding ? holding.quantity : 0;
    },

    // 启动定时更新
    startUpdates() {
      setInterval(() => {
        this.fetchStocks();
        if (this.selectedCompany) {
          this.fetchMarketData();
          this.fetchOrderBook();
          this.fetchHoldings();
        }
      }, 5000);
    },

    // 发行股票
    async issueStock() {
      if (!this.selectedCompany) {
        this.error = '请先选择公司';
        return;
      }

      try {
        this.loading = true;
        const response = await fetch('http://localhost:5010/api/stock/issue', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            company_id: this.selectedCompany.id,
            ...this.issueForm
          })
        });

        const data = await response.json();
        if (response.ok) {
          this.successMessage = '股票发行成功';
          this.fetchStocks();
        } else {
          this.error = data.error || '股票发行失败';
        }
      } catch (error) {
        this.error = '股票发行失败';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    // 获取我的订单
    async fetchMyOrders() {
      if (!this.selectedCompany) return;

      try {
        const response = await fetch(
          `http://localhost:5010/api/orders/${this.selectedCompany.id}`
        );
        const data = await response.json();
        this.myOrders = data;
      } catch (error) {
        console.error('获取订单失败：', error);
      }
    },

    // 获取交易历史
    async fetchTradeHistory() {
      if (!this.selectedCompany) return;

      try {
        const response = await fetch(
          `http://localhost:5010/api/transactions/${this.selectedCompany.id}`
        );
        const data = await response.json();
        this.tradeHistory = data;
      } catch (error) {
        console.error('获取交易历史失败：', error);
      }
    },

    // 撤销订单
    async cancelOrder(orderId) {
      try {
        this.loading = true;
        const response = await fetch(
          `http://localhost:5010/api/orders/${orderId}/cancel`,
          { method: 'POST' }
        );

        if (response.ok) {
          this.successMessage = '撤单成功';
          this.fetchMyOrders();
        } else {
          const data = await response.json();
          this.error = data.error || '撤单失败';
        }
      } catch (error) {
        this.error = '撤单失败';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    // 查看股票详情
    viewStockDetail(stock) {
      // TODO: 实现股票详情弹窗
    },

    // 获取订单状态文本
    getOrderStatus(status) {
      const statusMap = {
        'pending': '待成交',
        'partial': '部分成交',
        'filled': '已成交',
        'cancelled': '已撤销'
      };
      return statusMap[status] || status;
    },

    // 更新市场统计数据
    updateMarketStats() {
      this.totalMarketValue = this.stocks.reduce(
        (sum, stock) => sum + stock.current_price * stock.total_shares, 
        0
      );
      this.todayVolume = this.stocks.reduce(
        (sum, stock) => sum + stock.volume * stock.current_price,
        0
      );
      this.listedCompanies = this.stocks.length;
    }
  },
  watch: {
    stocks: {
      handler() {
        this.updateMarketStats();
      },
      deep: true
    }
  },
  mounted() {
    this.fetchCompanies();
    this.fetchStocks();
    this.startUpdates();
    if (this.selectedCompany) {
      this.fetchMyOrders();
      this.fetchTradeHistory();
    }
  }
}
</script>

<style>
/* 基础样式 */
.section {
  margin: 20px 0;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 导航栏 */
.nav-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f5f5f5;
}

.tab-btn.active {
  background: #3498db;
  color: white;
}

/* 表格样式 */
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

/* 交易所样式 */
.up { color: #00C851; }
.down { color: #ff4444; }

/* 交易中心布局 */
.trading-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

/* 订单簿样式 */
.order-lists {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 表单样式 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 按钮样式 */
button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #3498db;
  color: white;
  transition: all 0.3s;
}

button:hover {
  opacity: 0.9;
}

.buy-btn {
  background: #00C851;
}

.sell-btn {
  background: #ff4444;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.trade-dialog {
  background: white;
  padding: 20px;
  border-radius: 8px;
  min-width: 400px;
}

/* 消息提示 */
.error-message, .success-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px;
  border-radius: 4px;
  color: white;
  animation: slideIn 0.3s ease;
}

.error-message {
  background: #ff4444;
}

.success-message {
  background: #00C851;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* 市场概览 */
.market-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h4 {
  margin: 0;
  color: #666;
}

.stat-card p {
  margin: 10px 0 0;
  font-size: 24px;
  font-weight: bold;
  color: #3498db;
}

/* 股票发行 */
.stock-issue {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.issue-btn {
  background: #3498db;
  width: 100%;
}

/* 订单和交易历史 */
.my-orders, .trade-history {
  margin-top: 20px;
}

.buy { color: #00C851; }
.sell { color: #ff4444; }

.cancel-btn {
  background: #95a5a6;
}

.detail-btn {
  background: #3498db;
}

/* 表格响应式 */
@media (max-width: 1200px) {
  .stock-list table {
    display: block;
    overflow-x: auto;
  }
}
</style>
