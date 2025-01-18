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
            :disabled="loading"
          >
            <option value="">全部服务器</option>
            <option 
              v-for="server in servers" 
              :key="server.id" 
              :value="server.id"
              :disabled="server.status === 'unreachable'"
            >
              {{ server.name }} ({{ server.ip_address }})
              {{ server.status === 'unreachable' ? '(不可达)' : '' }}
            </option>
          </select>

          <!-- 容器选择 -->
          <template v-if="selectedServer">
            <label class="text-gray-700 dark:text-gray-300">选择容器:</label>
            <select
              v-model="selectedContainer"
              class="form-select rounded-md border-gray-300 shadow-sm"
              :disabled="loading || loadingContainers"
            >
              <option value="">该服务器所有容器</option>
              <option
                v-for="container in serverContainers"
                :key="container.id"
                :value="container.id"
              >
                {{ container.container_name || container.id }}
              </option>
            </select>
          </template>
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
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
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
            <h3 class="text-gray-500 text-sm">剩余流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(remainingTraffic) }}
            </p>
          </div>
        </div>
      </CardBox>

      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-yellow-100 dark:bg-yellow-800">
            <BaseIcon :path="mdiGauge" class="w-6 h-6 text-yellow-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">流量限制</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(trafficLimit) }}
            </p>
          </div>
        </div>
      </CardBox>
    </div>

    <!-- 流量图表 -->
    <CardBox class="h-96">
      <Line
        v-if="trafficData.length > 0"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="h-full flex items-center justify-center text-gray-500">
        暂无数据
      </div>
    </CardBox>

    <!-- 实时数据表格 -->
    <CardBox>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                容器名称
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
              <td class="px-6 py-4 whitespace-nowrap">{{ getContainerName(item.container_id) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.upload_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.download_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTime(item.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </CardBox>

    <div class="flex space-x-4">
      <div class="text-gray-600">
        流量限制: {{ formatTrafficWithUnit(trafficLimit) }}
      </div>
      <div class="text-gray-600">
        剩余流量: {{ formatTrafficWithUnit(remainingTraffic) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { 
  mdiUpload, 
  mdiDownload, 
  mdiChartLine,
  mdiRefresh,
  mdiPlay,
  mdiStop,
  mdiAlert,
  mdiGauge
} from '@mdi/js'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

// 初始化状态
const loading = ref(false)
const error = ref('')
const servers = ref([])
const selectedServer = ref('')
const trafficData = ref([])
const refreshInterval = ref(null)
const isAutoRefresh = ref(false)
const remainingTraffic = ref(0)
const trafficLimit = ref(0)
const selectedContainer = ref(null)  // 选中的容器
const serverContainers = ref([])     // 当前服务器的容器列表
const loadingContainers = ref(false) // 容器列表加载状态
const serverTrafficLimit = ref(0)

// 获取服务器列表
const fetchServers = async () => {
  try {
    console.log('开始获取服务器列表')
    const response = await api.getServers()
    console.log('获取服务器列表 - 原始响应:', response)

    if (response.success) {
      servers.value = response.servers.map(server => ({
        id: server.id,
        name: server.server_name,
        status: server.status || 'checking',
        ip_address: server.ip_address,
        total_traffic: server.total_traffic || 0
      }))
      console.log('处理后的服务器列表:', servers.value)
    } else {
      throw new Error(response.message || '获取服务器列表失败')
    }
  } catch (err) {
    console.error('获取服务器列表失败:', err)
    error.value = '获取服务器列表失败: ' + (err.message || '未知错误')
    servers.value = []
  }
}

// 获取服务器的容器列表
const fetchServerContainers = async (serverId) => {
  if (!serverId) return
  try {
    loadingContainers.value = true
    console.log('正在获取容器列表, serverId:', serverId)
    const response = await api.getServerContainers(serverId)
    console.log('容器列表响应:', response)
    
    if (response.success) {
      // 确保容器数据包含必要的字段
      serverContainers.value = response.containers.filter(container => 
        container.server_id === serverId
      ).map(container => ({
        id: container.id,
        container_name: container.container_name,
        server_ip: container.server_ip,
        node_exporter_port: container.node_exporter_port, // 这就是 metrics_port
        status: container.status
      }))
      console.log('处理后的容器列表:', serverContainers.value)
      selectedContainer.value = null
    } else {
      throw new Error(response.message || '获取容器列表失败')
    }
  } catch (error) {
    console.error('获取容器列表失败:', error)
    error.value = '获取容器列表失败: ' + error.message
    serverContainers.value = []
  } finally {
    loadingContainers.value = false
  }
}

// 监听服务器选择变化
watch(selectedServer, (newServerId) => {
  selectedContainer.value = null // 清空容器选择
  if (newServerId) {
    console.log('服务器选择变化，获取对应容器列表:', newServerId)
    fetchServerContainers(newServerId)
  } else {
    serverContainers.value = []
  }
})

// 修改获取流量数据的方法
const fetchTrafficData = async () => {
  try {
    if (loading.value) return
    loading.value = true
    error.value = ''
    
    let response
    console.log('开始获取流量数据')

    if (selectedContainer.value) {
      // 获取单个容器的流量数据
      response = await api.trafficApi.getContainerTraffic(selectedContainer.value)
      console.log('单个容器流量响应:', response)
      
      if (response.success) {
        // 转换响应格式以匹配图表需求
        response = {
          success: true,
          traffic_data: [{
            container_id: selectedContainer.value,
            ...response.traffic,
            timestamp: response.timestamp
          }]
        }
      }
    } else if (selectedServer.value) {
      // 获取服务器所有容器的流量数据
      const containerPromises = serverContainers.value.map(container => 
        api.trafficApi.getContainerTraffic(container.id)
      )
      const results = await Promise.all(containerPromises)
      
      response = {
        success: true,
        traffic_data: results
          .filter(r => r.success)
          .map(r => ({
            container_id: r.container_id,
            upload_traffic: r.traffic.upload_traffic,
            download_traffic: r.traffic.download_traffic,
            timestamp: r.timestamp
          }))
      }
    } else {
      // 获取所有容器的流量数据
      response = await api.trafficApi.getAllContainersTraffic()
    }
    
    console.log('最终流量数据:', response)
    
    if (response?.success) {
      trafficData.value = response.traffic_data.map(data => ({
        container_id: data.container_id,
        upload_traffic: data.upload_traffic || 0,
        download_traffic: data.download_traffic || 0,
        timestamp: data.timestamp
      }))
      
      // 更新流量限制和剩余流量
      updateTrafficLimits()
      
      error.value = ''
    } else {
      throw new Error(response?.message || '获取数据失败')
    }
  } catch (err) {
    console.error('获取流量数据失败:', err)
    error.value = '获取流量数据失败: ' + (err.message || '未知错误')
    trafficData.value = []
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

// 组件初始化
onMounted(async () => {
  await fetchServers()
})

// 组件卸载清理
onUnmounted(() => {
  stopAutoRefresh()
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
        backgroundColor: '#10B981',
        tension: 0.1,
        fill: false
      },
      {
        label: '下载流量',
        data: data.map(d => d.download_traffic / 1024 / 1024),
        borderColor: '#3B82F6',
        backgroundColor: '#3B82F6',
        tension: 0.1,
        fill: false
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
  },
  plugins: {
    legend: {
      position: 'top'
    }
  }
}

// 格式化流量数据
const formatTraffic = (bytes) => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// 在 script setup 中添加 getStatusText 方法
const getStatusText = (status) => {
  const statusMap = {
    'online': '在线',
    'unreachable': '不可达',
    'checking': '检查中',
    'healthy': '健康'  // 添加 healthy 状态的映射
  }
  return statusMap[status] || status
}

// 修改服务器状态指示器的样式类
const getStatusClass = (status) => {
  const classMap = {
    'online': 'bg-green-100 text-green-800',
    'healthy': 'bg-green-100 text-green-800',
    'unreachable': 'bg-red-100 text-red-800',
    'checking': 'bg-gray-100 text-gray-800'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800'
}

// 修改流量限制和剩余流量的计算逻辑
const updateTrafficLimits = () => {
  // 将字节转换为MB
  const bytesToMB = (bytes) => bytes / (1024 * 1024)
  const gbToMB = (gb) => gb * 1024  // 新增：GB转MB的转换函数

  // 计算已使用的总流量（MB）
  const totalTrafficMB = trafficData.value.reduce((sum, item) => 
    sum + bytesToMB(item.upload_traffic || 0) + bytesToMB(item.download_traffic || 0), 0
  )

  if (selectedContainer.value) {
    // 单个容器的流量限制
    const container = serverContainers.value.find(c => c.id === selectedContainer.value)
    if (container) {
      // 容器的总流量限制为上传和下载限制之和（MB）
      // 注意：container.max_upload_traffic 和 max_download_traffic 是以GB为单位
      const containerLimit = gbToMB(container.max_upload_traffic || 0) + gbToMB(container.max_download_traffic || 0)
      trafficLimit.value = containerLimit
      remainingTraffic.value = Math.max(0, containerLimit - totalTrafficMB)
    }
  } else if (selectedServer.value) {
    // 服务器的流量限制 (GB转MB)
    const server = servers.value.find(s => s.id === selectedServer.value)
    if (server?.total_traffic) {
      // server.total_traffic 是以GB为单位，需要转换为MB
      trafficLimit.value = gbToMB(server.total_traffic)
      remainingTraffic.value = Math.max(0, trafficLimit.value - totalTrafficMB)
    }
  } else {
    // 全部服务器流量 (GB转MB)
    const totalGBLimit = servers.value.reduce((sum, server) => sum + (server.total_traffic || 0), 0)
    trafficLimit.value = gbToMB(totalGBLimit)
    remainingTraffic.value = Math.max(0, trafficLimit.value - totalTrafficMB)
  }
}

// 监听选择变化
watch([selectedServer, selectedContainer], () => {
  updateTrafficLimits()
})

// 添加一个方法来获取容器名称
const getContainerName = (containerId) => {
  // 先在当前服务器的容器列表中查找
  const container = serverContainers.value.find(c => c.id === containerId)
  if (container) {
    return container.container_name || containerId
  }
  // 如果找不到，返回容器ID
  return containerId
}

// 修改流量格式化函数，统一使用MB单位显示
const formatTrafficWithUnit = (value) => {
  return `${value.toFixed(2)} MB`
}
</script> 
