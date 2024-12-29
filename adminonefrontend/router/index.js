import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    meta: {
      title: '登录'
    },
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue')
  },
  {
    meta: {
      title: '仪表盘',
      requiresAuth: true
    },
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue')
  },
  // 用户管理
  {
    meta: {
      title: '用户管理',
      requiresAuth: true
    },
    path: '/users',
    name: 'users',
    component: () => import('@/views/users/UserListView.vue')
  },
  {
    path: '/users/add',
    name: 'users-add',
    component: () => import('@/views/users/UserAddView.vue'),
    meta: { 
      title: '添加用户',
      requiresAuth: true
    }
  },
  // 容器管理
  {
    path: '/containers',
    name: 'containers',
    component: () => import('@/views/containers/ContainerListView.vue'),
    meta: {
      title: '容器列表',
      requiresAuth: true
    }
  },
  {
    path: '/containers/add',
    name: 'containers-add', 
    component: () => import('@/views/containers/ContainerAddView.vue'),
    meta: {
      title: '新建容器',
      requiresAuth: true
    }
  },
  // 流量监控
  {
    path: '/traffic',
    name: 'traffic',
    component: () => import('@/views/traffic/TrafficView.vue'),
    meta: {
      title: '流量监控',
      requiresAuth: true
    }
  },
  // 告警管理
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('@/views/alerts/AlertListView.vue'),
    meta: {
      title: '告警管理',
      requiresAuth: true 
    }
  },
  // 系统管理
  {
    path: '/system',
    name: 'system',
    component: () => import('@/views/system/SystemView.vue'),
    meta: {
      title: '系统管理',
      requiresAuth: true
    },
    children: [
      {
        path: 'logs',
        name: 'system-logs',
        component: () => import('@/views/system/LogsView.vue'),
        meta: { title: '系统日志' }
      },
      {
        path: 'ha',
        name: 'system-ha',
        component: () => import('@/views/system/HAView.vue'),
        meta: { title: '高可用配置' }
      }
    ]
  },
  // 序列号管理
  {
    path: '/serial',
    name: 'serial',
    component: () => import('@/views/serial/SerialListView.vue'),
    meta: {
      title: '序列号管理',
      requiresAuth: true
    }
  },
  // 租赁管理
  {
    path: '/rental',
    name: 'rental',
    component: () => import('@/views/rental/RentalListView.vue'),
    meta: {
      title: '租赁管理',
      requiresAuth: true
    }
  },
  // ACL管理
  {
    path: '/acl',
    name: 'acl',
    component: () => import('@/views/acl/AclListView.vue'),
    meta: {
      title: 'ACL管理',
      requiresAuth: true
    }
  },
  {
    path: '/acl/generate',
    name: 'acl-generate',
    component: () => import('@/views/acl/AclGenerateView.vue'),
    meta: {
      title: '生成ACL',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
