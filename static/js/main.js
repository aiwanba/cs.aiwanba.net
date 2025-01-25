// 全局工具函数
function formatMoney(amount) {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
    }).format(amount);
}

function formatNumber(num) {
    return new Intl.NumberFormat('zh-CN').format(num);
}

// 全局错误处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    alert('操作失败，请重试');
});

// 自动刷新功能
function setupAutoRefresh() {
    // 每30秒刷新一次数据
    setInterval(() => {
        if (typeof loadCompanies === 'function') {
            loadCompanies();
        }
        if (typeof loadHoldings === 'function') {
            loadHoldings();
        }
    }, 30000);
}

// 页面加载完成后设置自动刷新
document.addEventListener('DOMContentLoaded', setupAutoRefresh); 