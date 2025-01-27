import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
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
  } else {
    next()
  }
})

export default router 