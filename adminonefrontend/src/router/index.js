import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/auth/LoginView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SerialManageView from '@/views/serial/SerialManageView.vue'
import ServerHealthView from '@/views/servers/ServerHealthView.vue'
import AclLogsView from '@/views/acl/AclLogsView.vue'

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
      requiresAuth: true,
      roles: ['admin', 'user', 'super_admin', 'distributor']
    }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: ProfileView
  },
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
      requiresAuth: true,
      title: '序列号统计'
    }
  },
  {
    path: '/users',
    children: [
      {
        path: '',  // 用户列表
        name: 'users.list',
        component: () => import('@/views/users/UserListView.vue'),
        meta: { 
          requiresAuth: true,
          roles: ['admin', 'super_admin'],
          layout: 'authenticated'
        }
      },
      {
        path: 'add',  // 添加用户
        name: 'users.add',
        component: () => import('@/views/users/UserAddView.vue'),
        meta: { 
          requiresAuth: true,
          layout: 'authenticated',
          title: '添加用户'
        }
      }
    ]
  },
  {
    path: '/containers',
    name: 'containers',
    component: () => import('@/views/containers/ContainerListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/containers/add',
    name: 'containers.add',
    component: () => import('@/views/containers/ContainerAddView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/acl',
    name: 'acl.list',
    component: () => import('@/views/acl/AclListView.vue'),
    meta: { 
      requiresAuth: true,
      layout: 'authenticated'
    }
  },
  {
    path: '/acl/generate',
    name: 'acl.generate',
    component: () => import('@/views/acl/AclGenerateView.vue'),
    meta: { 
      requiresAuth: true,
      layout: 'authenticated'
    }
  },
  {
    path: '/acl/edit/:id',
    name: 'acl.edit',
    component: () => import('@/views/acl/AclGenerateView.vue'),
    meta: { 
      requiresAuth: true,
      layout: 'authenticated'
    }
  },
  {
    path: '/acl/logs',
    name: 'acl-logs',
    component: AclLogsView,
    meta: {
      requiresAuth: true
    }
  },
  {
    meta: {
      title: '服务器健康状态'
    },
    path: '/servers/health',
    name: 'servers-health',
    component: ServerHealthView
  },
  {
    path: '/rental',
    children: [
      {
        path: '',  // 默认路由，显示租赁列表
        name: 'rental.list',
        component: () => import('@/views/rental/RentalListView.vue'),
        meta: {
          requiresAuth: true,
          layout: 'authenticated'
        }
      },
      {
        path: 'expiry',
        name: 'rental.expiry',
        component: () => import('@/views/rental/RentalExpiryView.vue'),
        meta: {
          requiresAuth: true,
          layout: 'authenticated'
        }
      },
      {
        path: 'history',
        name: 'rental.history', 
        component: () => import('@/views/rental/RentalHistoryView.vue'),
        meta: {
          requiresAuth: true,
          layout: 'authenticated'
        }
      }
    ]
  },
  {
    path: '/traffic',
    component: () => import('@/views/traffic/TrafficLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: { name: 'traffic.realtime' }
      },
      {
        path: 'realtime',
        name: 'traffic.realtime',
        component: () => import('@/views/traffic/TrafficRealtimeView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'history',
        name: 'traffic.history',
        component: () => import('@/views/traffic/TrafficHistoryView.vue'),
        meta: { 
          requiresAuth: true,
          title: '历史记录'
        }
      },
      {
        path: 'stats',
        name: 'traffic.stats',
        component: () => import('@/views/traffic/TrafficStatsView.vue'),
        meta: { 
          requiresAuth: true,
          title: '统计分析'
        }
      }
    ]
  },
  {
    path: '/rental/expiry',
    name: 'rental-expiry',
    component: () => import('@/views/rental/RentalExpiryView.vue'),
    meta: {
      requiresAuth: true,
      roles: ['admin', 'super_admin']
    }
  },
  {
    path: '/alerts',
    component: () => import('@/views/alerts/AlertLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'alerts.list',
        component: () => import('@/views/alerts/AlertListView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'alerts.settings',
        component: () => import('@/views/alerts/AlertSettingsView.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/adminonefrontend/'),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user'))
  
  if (to.meta.requiresAuth) {
    if (!token) {
      // 没有 token，重定向到登录页
      next('/login')
      return
    }
    
    // 检查角色权限
    if (to.meta.roles && !to.meta.roles.includes(user?.role)) {
      console.warn('权限不足')
      next('/dashboard') // 或者跳转到无权限页面
      return
    }
    
    next()
  } else if (to.path === '/login' && token) {
    // 已登录用户访问登录页，重定向到仪表盘
    next('/dashboard')
  } else {
    next()
  }
})

// 添加全局错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    window.location.reload()
  }
})

export default router
