# 金融模拟系统前端

## 项目介绍
这是一个基于 Vue 3 + Element Plus 开发的金融模拟系统前端项目，提供公司管理、股票交易、银行业务等功能。

## 技术栈
- Vue 3
- Vue Router
- Element Plus
- Axios
- WebSocket
- ECharts

## 开发环境
- Node.js >= 16
- npm >= 8

## 项目结构
```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 公共组件
│   ├── composables/     # 组合式函数
│   ├── router/          # 路由配置
│   ├── services/        # 服务层
│   ├── store/           # 状态管理
│   ├── utils/           # 工具函数
│   └── views/           # 页面组件
├── public/              # 公共文件
├── .env                 # 环境变量
├── package.json         # 项目配置
└── vite.config.js       # Vite配置
```

## 快速开始

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

## 功能模块

### 公司管理
- 公司列表
- 公司创建
- 公司详情
- 股权管理

### 股票交易
- 行情展示
- 交易下单
- 持仓管理
- 订单记录

### 银行业务
- 账户管理
- 存取款
- 贷款服务
- 转账汇款

## 开发规范

### 命名规范
- 组件名：PascalCase
- 文件名：kebab-case
- 变量名：camelCase
- 常量名：UPPER_CASE

### 代码风格
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化
- 遵循 Vue 3 组合式 API 风格指南

### Git提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

## 部署说明

### 环境要求
- Nginx >= 1.18
- HTTPS证书（用于WebSocket安全连接）

### 部署步骤
1. 构建项目
```bash
npm run build
```

2. 配置Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend-server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://websocket-server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. 启动服务
```bash
nginx -s reload
```

## 性能优化

### 代码分割
- 路由懒加载
- 组件异步加载
- 第三方库按需导入

### 缓存策略
- 浏览器缓存
- 本地存储
- 接口数据缓存

### 渲染优化
- 虚拟列表
- 延迟加载
- 防抖节流

## 错误处理

### 全局错误处理
- API错误统一处理
- Vue错误捕获
- Promise异常处理

### 用户提示
- 友好的错误提示
- 加载状态反馈
- 操作结果通知

## 安全措施

### 数据安全
- Token认证
- 敏感数据加密
- XSS防护

### 操作安全
- 防重复提交
- 操作确认
- 权限控制 