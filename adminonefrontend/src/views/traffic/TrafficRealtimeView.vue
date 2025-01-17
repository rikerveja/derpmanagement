<template>
  <div class="grid gap-6">
    <!-- 服务器状态指示器 -->
    <div class="flex flex-wrap gap-2" v-if="servers.length > 0">
      <div v-for="server in servers" 
           :key="server.id"
           class="px-3 py-1 rounded-full text-sm"
           :class="{
             'bg-green-100 text-green-800': server.status === 'online',
             'bg-red-100 text-red-800': server.status === 'unreachable',
             'bg-gray-100 text-gray-800': server.status === 'checking'
           }"
      >
        {{ server.name }}: {{ getStatusText(server.status) }}
      </div>
    </div>

    <!-- 控制栏 -->
    <CardBox>
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <label class="text-gray-700 dark:text-gray-300">选择服务器:</label>
          <select 
            v-model="selectedServer"
            class="form-select rounded-md border-gray-300 shadow-sm"
          >
            <option value="">全部服务器</option>
            <option v-for="server in servers" 
                    :key="server.id" 
                    :value="server.id"
                    :disabled="server.status === 'unreachable'"
            >
              {{ server.name }} 
              {{ server.status === 'unreachable' ? '(不可达)' : '' }}
            </option>
          </select>
        </div>
        <div class="flex space-x-2">
          <BaseButton
            :color="isAutoRefresh ? 'danger' : 'success'"
            :label="isAutoRefresh ? '停止自动刷新' : '开启自动刷新'"
            :icon="isAutoRefresh ? mdiStop : mdiPlay"
            @click="toggleAutoRefresh"
          />
          <BaseButton
            color="info"
            label="刷新"
            :icon="mdiRefresh"
            :loading="loading"
            @click="fetchTrafficData"
          />
        </div>
      </div>
    </CardBox>

    <!-- 错误提示 -->
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
      <span class="block sm:inline">{{ error }}</span>
      <button @click="error = ''" class="absolute top-0 bottom-0 right-0 px-4 py-3">
        <span class="sr-only">关闭</span>
        <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
          <title>关闭</title>
          <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
        </svg>
      </button>
    </div>

    <!-- 流量概览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100 dark:bg-green-800">
            <BaseIcon :path="mdiUpload" class="w-6 h-6 text-green-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">上传流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(totalUpload) }}
            </p>
          </div>
        </div>
      </CardBox>
      
      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100 dark:bg-blue-800">
            <BaseIcon :path="mdiDownload" class="w-6 h-6 text-blue-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">下载流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(totalDownload) }}
            </p>
          </div>
        </div>
      </CardBox>
      
      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-100 dark:bg-purple-800">
            <BaseIcon :path="mdiChartLine" class="w-6 h-6 text-purple-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">总流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(totalUpload + totalDownload) }}
            </p>
          </div>
        </div>
      </CardBox>
    </div>

    <!-- 流量图表 -->
    <CardBox>
      <Line 
        :data="chartData" 
        :options="chartOptions"
        class="h-80"
      />
    </CardBox>

    <!-- 实时数据表格 -->
    <CardBox>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                容器ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                上传流量
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                下载流量
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                时间
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="item in trafficData" :key="item.timestamp">
              <td class="px-6 py-4 whitespace-nowrap">{{ item.container_id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.upload_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.download_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTime(item.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </CardBox>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import { 
  mdiUpload, 
  mdiDownload, 
  mdiChartLine,
  mdiRefresh,
  mdiPlay,
  mdiStop,
  mdiAlert
} from '@mdi/js'
import CardBox from '@/components/CardBox.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseButton from '@/components/BaseButton.vue'
import api from '@/services/api'

const servers = ref([])
const selectedServer = ref('')
const trafficData = ref([])
const refreshInterval = ref(null)
const loading = ref(false)
const error = ref(null)
const isAutoRefresh = ref(false)
const serverCheckPromises = ref([])

// 获取服务器列表
const fetchServers = async () => {
  error.value = null
  loading.value = true
  
  try {
    const response = await api.getServers()
    if (response.success) {
      servers.value = response.servers.map(server => ({
        ...server,
        status: 'checking'
      }))
      // 并行检查所有服务器状态
      await checkAllServersStatus()
    }
  } catch (err) {
    error.value = '获取服务器列表失败: ' + (err.message || '未知错误')
    servers.value = []
  } finally {
    loading.value = false
  }
}

// 并行检查所有服务器状态
const checkAllServersStatus = async () => {
  const checkPromises = servers.value.map(async server => {
    try {
      const response = await api.checkServerStatus(server.id)
      server.status = response.success ? 'online' : 'unreachable'
    } catch (err) {
      server.status = 'unreachable'
      console.error(`服务器 ${server.name} 状态检查失败:`, err)
    }
  })

  // 使用 Promise.allSettled 确保所有检查都完成
  await Promise.allSettled(checkPromises)
}

// 获取流量数据（带重试机制）
const fetchTrafficData = async () => {
  try {
    if (loading.value) return; // 防止重复请求
    
    loading.value = true
    error.value = ''
    
    // 添加超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时
    
    const response = await api.getTrafficData(selectedServer.value, {
      signal: controller.signal
    })
    
    clearTimeout(timeoutId);
    
    if (response.success) {
      trafficData.value = response.data
      error.value = ''
    } else {
      error.value = response.message || '获取数据失败'
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      error.value = '请求超时，请稍后重试'
    } else {
      error.value = err.message || '获取数据失败'
    }
  } finally {
    loading.value = false
  }
}

// 切换自动刷新（带安全检查）
const toggleAutoRefresh = () => {
  if (isAutoRefresh.value) {
    stopAutoRefresh()
  } else {
    startAutoRefresh()
  }
}

const startAutoRefresh = async () => {
  if (refreshInterval.value) {
    stopAutoRefresh()
  }
  
  if (selectedServer.value) {
    const server = servers.value.find(s => s.id === selectedServer.value)
    if (server?.status === 'unreachable') {
      error.value = '无法启动自动刷新：所选服务器不可用'
      return
    }
  }
  
  await fetchTrafficData()
  refreshInterval.value = setInterval(() => {
    if (!loading.value) {
      fetchTrafficData()
    }
  }, 30000) // 30秒刷新一次
  isAutoRefresh.value = true
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  isAutoRefresh.value = false
}

// 监听服务器选择变化
watch(selectedServer, async (newValue) => {
  if (newValue) {
    const server = servers.value.find(s => s.id === newValue)
    if (server?.status === 'unreachable') {
      error.value = '所选服务器当前不可用'
      return
    }
  }
  if (isAutoRefresh.value) {
    stopAutoRefresh()
    startAutoRefresh()
  } else {
    await fetchTrafficData()
  }
})

// 组件初始化
onMounted(async () => {
  await fetchServers()
})

// 组件卸载清理
onUnmounted(() => {
  stopAutoRefresh()
  if (controller.value) {
    controller.value.abort()
  }
  // 取消所有未完成的服务器状态检查
  serverCheckPromises.value.forEach(promise => {
    if (promise.cancel) {
      promise.cancel()
    }
  })
})

// 计算总流量
const totalUpload = computed(() => 
  trafficData.value.reduce((sum, item) => sum + item.upload_traffic, 0)
)
const totalDownload = computed(() => 
  trafficData.value.reduce((sum, item) => sum + item.download_traffic, 0)
)

// 图表配置
const chartData = computed(() => {
  const maxDataPoints = 50 // 最多显示50个数据点
  const data = trafficData.value.slice(-maxDataPoints)
  
  return {
    labels: data.map(d => formatTime(d.timestamp)),
    datasets: [
      {
        label: '上传流量',
        data: data.map(d => d.upload_traffic / 1024 / 1024),
        borderColor: '#10B981',
        tension: 0.1
      },
      {
        label: '下载流量',
        data: data.map(d => d.download_traffic / 1024 / 1024),
        borderColor: '#3B82F6',
        tension: 0.1
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: '流量 (MB)'
      }
    }
  }
}

// 格式化流量数据
const formatTraffic = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}
</script> 