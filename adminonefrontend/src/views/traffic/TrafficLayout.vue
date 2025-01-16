<template>
  <LayoutAuthenticated>
    <SectionMain>
      <div class="grid gap-6">
        <!-- 导航标签 -->
        <div class="flex space-x-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <router-link 
            v-for="nav in navigation" 
            :key="nav.name"
            :to="nav.to"
            class="px-4 py-2 rounded-md"
            :class="[
              $route.name === nav.name 
                ? 'bg-primary-500 text-white' 
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            {{ nav.label }}
          </router-link>
        </div>
        
        <!-- 子路由内容 -->
        <router-view></router-view>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'

const navigation = [
  { name: 'traffic.realtime', to: '/traffic/realtime', label: '实时监控' },
  { name: 'traffic.history', to: '/traffic/history', label: '历史记录' },
  { name: 'traffic.stats', to: '/traffic/stats', label: '统计分析' }
]
</script> 