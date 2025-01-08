import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/auth/LoginView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SerialManageView from '@/views/serial/SerialManageView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: ProfileView
  },
  // 重定向根路径到登录页
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/servers/list',
    name: 'servers.list',
    component: () => import('@/views/servers/ServerListView.vue'),
    meta: { 
      requiresAuth: true,
      layout: 'authenticated'
    }
  },
  {
    path: '/serials/manage',
    name: 'SerialManage',
    component: SerialManageView,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/serials/stats',
    name: 'SerialStats',
    component: () => import('@/views/serial/SerialStatsView.vue'),
    meta: {
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory('/adminonefrontend/'),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要认证但没有 token，重定向到登录页
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录用户访问登录页，重定向到仪表盘
    next('/dashboard')
  } else {
    next()
  }
})

export default router
