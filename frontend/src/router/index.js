import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: '/company',
        component: () => import('../views/company/CompanyLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: 'list',
            name: 'CompanyList',
            component: () => import('../views/company/CompanyList.vue')
          },
          {
            path: 'create',
            name: 'CompanyCreate',
            component: () => import('../views/company/CompanyCreate.vue')
          },
          {
            path: 'detail/:id',
            name: 'CompanyDetail',
            component: () => import('../views/company/CompanyDetail.vue')
          }
        ]
      },
      {
        path: '/stock',
        component: () => import('../views/stock/StockLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: 'market',
            name: 'StockMarket',
            component: () => import('../views/stock/StockMarket.vue')
          },
          {
            path: 'positions',
            name: 'StockPositions',
            component: () => import('../views/stock/StockPositions.vue')
          },
          {
            path: 'orders',
            name: 'StockOrders',
            component: () => import('../views/stock/StockOrders.vue')
          }
        ]
      },
      {
        path: '/bank',
        component: () => import('../views/bank/BankLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: 'accounts',
            name: 'BankAccounts',
            component: () => import('../views/bank/BankAccounts.vue')
          },
          {
            path: 'loan',
            name: 'BankLoan',
            component: () => import('../views/bank/BankLoan.vue')
          },
          {
            path: 'transfer',
            name: 'BankTransfer',
            component: () => import('../views/bank/BankTransfer.vue')
          }
        ]
      },
      {
        path: '/settings',
        component: () => import('../views/settings/SystemSettings.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (token && (to.path === '/login' || to.path === '/register')) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router 