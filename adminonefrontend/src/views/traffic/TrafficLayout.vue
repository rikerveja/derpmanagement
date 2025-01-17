<template>
  <LayoutAuthenticated>
    <SectionMain>
      <!-- 导航标签 -->
      <div class="mb-6">
        <div class="flex space-x-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <router-link 
            v-for="nav in navigation" 
            :key="nav.name"
            :to="nav.to"
            class="px-4 py-2 rounded-md"
            :class="[
              $route.name === nav.name 
                ? 'bg-blue-500 text-white' 
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            ]"
          >
            {{ nav.label }}
          </router-link>
        </div>
      </div>
      
      <!-- 子路由内容 -->
      <Suspense>
        <template #default>
          <router-view></router-view>
        </template>
        <template #fallback>
          <div class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        </template>
      </Suspense>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'

const navigation = [
  { name: 'traffic.realtime', to: '/traffic/realtime', label: '实时监控' },
  { name: 'traffic.history', to: '/traffic/history', label: '历史记录' },
  { name: 'traffic.stats', to: '/traffic/stats', label: '统计分析' }
]

onMounted(() => {
  console.log('TrafficLayout mounted')
})
</script> 