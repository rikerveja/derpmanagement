<template>
  <div class="grid gap-6">
    <!-- 统计类型选择 -->
    <CardBox>
      <div class="flex items-center space-x-4">
        <label class="text-gray-700 dark:text-gray-300">统计类型:</label>
        <select 
          v-model="statsType"
          class="form-select rounded-md border-gray-300 shadow-sm"
        >
          <option value="user">按用户统计</option>
          <option value="server">按服务器统计</option>
        </select>

        <template v-if="statsType === 'user'">
          <label class="text-gray-700 dark:text-gray-300">选择用户:</label>
          <select v-model="selectedId" class="form-select">
            <option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.username }}
            </option>
          </select>
        </template>

        <template v-else>
          <label class="text-gray-700 dark:text-gray-300">选择服务器:</label>
          <select v-model="selectedId" class="form-select">
            <option v-for="server in servers" :key="server.id" :value="server.id">
              {{ server.name }}
            </option>
          </select>
        </template>
      </div>
    </CardBox>

    <!-- 统计图表 -->
    <CardBox class="h-96">
      <!-- 图表组件 -->
    </CardBox>

    <!-- 统计数据表格 -->
    <CardBox>
      <!-- 数据表格 -->
    </CardBox>

    <!-- 超流量用户警告 -->
    <CardBox v-if="overlimitUsers.length > 0" class="bg-red-50">
      <h3 class="text-red-700 font-medium mb-4">超流量用户警告</h3>
      <div class="space-y-2">
        <div v-for="user in overlimitUsers" :key="user.container_id" class="flex justify-between items-center">
          <span>容器 ID: {{ user.container_id }}</span>
          <span class="text-red-600">超出: {{ formatTraffic(-user.remaining_traffic) }}</span>
        </div>
      </div>
    </CardBox>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { mdiChartLine, mdiRefresh, mdiAlert, mdiMagnify } from '@mdi/js'
import api from '@/services/api'

const statsType = ref('user')
const selectedId = ref('')
const users = ref([])
const servers = ref([])
const statsData = ref([])
const summary = ref(null)
const loading = ref(false)
const error = ref(null)
const overlimitUsers = ref([])

// 获取用户和服务器列表
const fetchOptions = async () => {
  try {
    const [usersResponse, serversResponse] = await Promise.all([
      api.getUsers(),
      api.getServers()
    ])
    
    if (usersResponse.success) {
      users.value = usersResponse.users
    }
    if (serversResponse.success) {
      servers.value = serversResponse.servers
    }
  } catch (err) {
    error.value = '获取选项数据失败: ' + err.message
  }
}

// 获取统计数据
const fetchStats = async () => {
  const id = statsType.value === 'user' ? selectedId.value : selectedId.value
  if (!id) {
    error.value = `请选择${statsType.value === 'user' ? '用户' : '服务器'}`
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await api.getTrafficStats({
      user_id: statsType.value === 'user' ? id : undefined,
      server_id: statsType.value === 'server' ? id : undefined
    })

    if (response.success) {
      statsData.value = statsType.value === 'user' ? response.user_traffic : response.server_traffic
      summary.value = statsType.value === 'user' ? response.user_summary : response.server_summary
    } else {
      throw new Error(response.message || '获取统计数据失败')
    }
  } catch (err) {
    error.value = err.message
    statsData.value = []
    summary.value = null
  } finally {
    loading.value = false
  }
}

// 监听统计类型变化
watch(statsType, () => {
  selectedId.value = ''
  statsData.value = []
  summary.value = null
  error.value = null
})

// 图表配置
const chartData = computed(() => ({
  labels: statsData.value.map(d => formatTime(d.timestamp)),
  datasets: [
    {
      label: '上传流量',
      data: statsData.value.map(d => d.upload_traffic / 1024 / 1024),
      borderColor: '#10B981',
      tension: 0.1
    },
    {
      label: '下载流量',
      data: statsData.value.map(d => d.download_traffic / 1024 / 1024),
      borderColor: '#3B82F6',
      tension: 0.1
    }
  ]
}))

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

// 格式化函数
const formatTraffic = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// 获取超流量用户
const fetchOverlimitUsers = async () => {
  try {
    const response = await api.getOverLimitUsers()
    
    if (response.success) {
      overlimitUsers.value = response.users
    } else {
      throw new Error(response.message || '获取超流量用户失败')
    }
  } catch (err) {
    error.value = err.message
    overlimitUsers.value = []
  }
}

onMounted(() => {
  fetchOptions()
  fetchOverlimitUsers()
})
</script> 