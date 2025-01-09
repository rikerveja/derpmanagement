import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import LoginView from '@/views/auth/LoginView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SerialManageView from '@/views/serial/SerialManageView.vue'

const routes: RouteRecordRaw[] = [
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
    path: '/containers',
    name: 'containers',
    component: async () => await import('@/views/containers/ContainerListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/containers/add',
    name: 'containers.add',
    component: async () => await import('@/views/containers/ContainerAddView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/adminonefrontend/'),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

router.onError((error: Error) => {
  console.error('路由错误:', error)
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    window.location.reload()
  }
})

export default router 
