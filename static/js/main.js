// API基础URL
const API_BASE_URL = '';

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 默认显示市场页面
    showSection('market');
    // 加载市场数据
    loadMarketData();
    // 启动WebSocket连接
    connectWebSocket();
});

// 显示不同部分
function showSection(sectionName) {
    // 隐藏所有section
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    // 显示选中的section
    document.getElementById(`${sectionName}-section`).style.display = 'block';
    
    // 加载相应数据
    switch(sectionName) {
        case 'market':
            loadMarketData();
            break;
        case 'bank':
            loadBankAccount();
            break;
        case 'notifications':
            loadNotifications();
            break;
    }
}

// 加载市场数据
async function loadMarketData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/market`);
        const data = await response.json();
        
        const tableBody = document.getElementById('market-data');
        tableBody.innerHTML = data.companies.map(company => `
            <tr>
                <td>${company.name}</td>
                <td>${company.stock_price}</td>
                <td>${company.volume || 0}</td>
                <td>
                    <button onclick="showTradeDialog(${company.id})" class="btn">交易</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        showNotification('加载市场数据失败', 'error');
    }
}

// 创建公司
document.getElementById('company-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/company`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification('公司创建成功', 'info');
            showSection('market');
        } else {
            const error = await response.json();
            showNotification(error.error, 'error');
        }
    } catch (error) {
        showNotification('创建公司失败', 'error');
    }
});

// 加载银行账户信息
async function loadBankAccount() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/bank/account/balance`);
        const data = await response.json();
        
        document.getElementById('account-info').innerHTML = `
            <div class="account-balance">
                <h3>活期余额：${data.balance}元</h3>
                <h4>定期存款：</h4>
                <ul>
                    ${data.time_deposits.map(d => `
                        <li>金额：${d.amount}元，到期日：${new Date(d.end_date).toLocaleDateString()}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    } catch (error) {
        showNotification('加载账户信息失败', 'error');
    }
}

// 创建定期存款
async function createDeposit() {
    const amount = document.getElementById('deposit-amount').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/bank/deposit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: parseFloat(amount) })
        });
        
        if (response.ok) {
            showNotification('定期存款创建成功', 'info');
            loadBankAccount();
        } else {
            const error = await response.json();
            showNotification(error.error, 'error');
        }
    } catch (error) {
        showNotification('创建定期存款失败', 'error');
    }
}

// 加载消息
async function loadNotifications() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/notifications`);
        const notifications = await response.json();
        
        document.getElementById('notifications-list').innerHTML = notifications.map(n => `
            <div class="notification ${n.level}">
                <h4>${n.title}</h4>
                <p>${n.content}</p>
                <small>${new Date(n.created_at).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (error) {
        showNotification('加载消息失败', 'error');
    }
}

// 显示消息提醒
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// WebSocket连接
function connectWebSocket() {
    const socket = io();
    
    socket.on('message', function(data) {
        showNotification(data.message, data.type);
        
        // 根据消息类型更新相应的数据
        if (data.type === 'market') {
            loadMarketData();
        }
    });
} 