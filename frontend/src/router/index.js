import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { ElMessage } from 'element-plus'
import store from '../store'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue'),
          meta: { requiresAuth: true }
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
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = store.state.user
  
  if (to.path === '/login' || to.path === '/register') {
    if (token && user) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }
  
  if (to.meta.requiresAuth) {
    if (!token || !user) {
      ElMessage.warning('请先登录')
      next('/login')
    } else {
      next()
    }
    return
  }
  
  next()
})

export default router 