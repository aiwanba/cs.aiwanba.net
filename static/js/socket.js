// WebSocket连接管理
class SocketManager {
    constructor() {
        this.socket = io();
        this.initializeEventHandlers();
    }
    
    initializeEventHandlers() {
        // 连接事件
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.joinRoom('market');  // 加入市场数据房间
        });
        
        // 市场数据更新
        this.socket.on('market_update', (data) => {
            this.handleMarketUpdate(data);
        });
        
        // 交易更新
        this.socket.on('transaction_update', (data) => {
            this.handleTransactionUpdate(data);
        });
        
        // 新闻更新
        this.socket.on('news_update', (data) => {
            this.handleNewsUpdate(data);
        });
    }
    
    joinRoom(room) {
        this.socket.emit('join', { room: room });
    }
    
    leaveRoom(room) {
        this.socket.emit('leave', { room: room });
    }
    
    handleMarketUpdate(data) {
        // 更新市场数据显示
        const marketTable = document.getElementById('market-table');
        if (marketTable) {
            const tbody = marketTable.querySelector('tbody');
            tbody.innerHTML = '';
            
            data.data.forEach(company => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${company.name}</td>
                    <td>${company.current_price.toFixed(2)}</td>
                    <td>${company.available_shares}</td>
                    <td>${company.market_value.toFixed(2)}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }
    
    handleTransactionUpdate(data) {
        // 更新交易历史显示
        const transactionList = document.getElementById('transaction-list');
        if (transactionList) {
            const item = document.createElement('div');
            item.className = 'transaction-item';
            item.innerHTML = `
                <div class="transaction-type ${data.type}">${data.type}</div>
                <div class="transaction-details">
                    <span>${data.company_name}</span>
                    <span>${data.shares}股</span>
                    <span>￥${data.price}</span>
                </div>
                <div class="transaction-time">${data.created_at}</div>
            `;
            transactionList.insertBefore(item, transactionList.firstChild);
        }
    }
    
    handleNewsUpdate(data) {
        // 更新新闻显示
        const newsList = document.getElementById('news-list');
        if (newsList) {
            const item = document.createElement('div');
            item.className = 'news-item';
            item.innerHTML = `
                <h3>${data.title}</h3>
                <p>${data.content}</p>
                <div class="news-meta">
                    <span>${data.type}</span>
                    <span>${data.created_at}</span>
                </div>
            `;
            newsList.insertBefore(item, newsList.firstChild);
        }
    }
}

// 初始化WebSocket管理器
const socketManager = new SocketManager(); 