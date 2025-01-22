<template>
  <div class="grid gap-6">
    <!-- 用户选择器 -->
    <CardBox>
      <div class="flex items-center space-x-4">
        <label class="text-gray-700 dark:text-gray-300">选择用户:</label>
        <div class="relative flex-1 max-w-md">
          <input
            v-model="userSearchQuery"
            type="text"
            class="w-full px-3 py-2 border rounded-md pr-10"
            placeholder="搜索用户名或邮箱..."
            @input="handleSearch"
          />
          <BaseIcon
            :path="mdiMagnify"
            class="absolute right-3 top-2.5 text-gray-400"
            size="20"
          />
        </div>
        <select 
          v-model="selectedUserId"
          class="form-select rounded-md border-gray-300 shadow-sm min-w-[200px]"
          @change="handleUserSelect"
          :disabled="loadingUsers"
        >
          <option value="">{{ loadingUsers ? '加载中...' : '请选择用户' }}</option>
          <option 
            v-for="user in filteredUsers" 
            :key="user.id" 
            :value="user.id"
          >
            {{ user.username }} ({{ user.email }})
          </option>
        </select>
      </div>
    </CardBox>

    <!-- 历史数据图表 -->
    <CardBox class="h-96">
      <Line
        v-if="historyData.length > 0"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="h-full flex items-center justify-center text-gray-500">
        {{ loading ? '加载中...' : '请选择用户查看历史数据' }}
      </div>
    </CardBox>

    <!-- 历史数据表格 -->
    <CardBox>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                时间
              </th>
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
                剩余流量
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="5" class="px-6 py-4 text-center">
                <div class="flex justify-center">
                  <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                </div>
              </td>
            </tr>
            <tr v-else-if="historyData.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                暂无数据
              </td>
            </tr>
            <tr v-for="(record, index) in historyData" 
                :key="index"
                class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatTime(record.timestamp) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ record.container_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="JSON.stringify(record.upload_traffic)">
                  {{ formatTraffic(record.upload_traffic) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="JSON.stringify(record.download_traffic)">
                  {{ formatTraffic(record.download_traffic) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :title="JSON.stringify(record.remaining_traffic)">
                  {{ formatTraffic(record.remaining_traffic) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </CardBox>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
import CardBox from '@/components/CardBox.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { mdiMagnify } from '@mdi/js'
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

// 状态变量
const users = ref([])
const selectedUserId = ref('')
const userSearchQuery = ref('')
const historyData = ref([])
const loading = ref(false)
const loadingUsers = ref(false)

// 获取用户列表
const fetchUsers = async () => {
  try {
    loadingUsers.value = true
    const response = await api.getAllUsers()
    console.log('用户列表响应:', response) // 调试用
    
    if (response.success) {
      // 直接使用返回的用户数据
      users.value = response.users || []
    } else {
      console.error('获取用户列表失败:', response.message)
      users.value = []
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    users.value = []
  } finally {
    loadingUsers.value = false
  }
}

// 过滤用户列表
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return users.value
  const query = userSearchQuery.value.toLowerCase()
  return users.value.filter(user => {
    const username = user.username?.toLowerCase() || ''
    const email = user.email?.toLowerCase() || ''
    return username.includes(query) || email.includes(query)
  })
})

// 获取流量历史数据
const fetchTrafficHistory = async () => {
  if (!selectedUserId.value) return
  
  try {
    loading.value = true
    const response = await api.getTrafficHistory(selectedUserId.value)
    console.log('获取到的历史数据:', response)
    
    if (response.success) {
      // 修正：使用 history_data 而不是 data
      historyData.value = response.history_data.map(record => ({
        timestamp: record.timestamp,
        container_id: record.container_id,
        upload_traffic: Number(record.upload_traffic),
        download_traffic: Number(record.download_traffic),
        remaining_traffic: Number(record.remaining_traffic)
      }))
      console.log('处理后的历史数据:', historyData.value)
    }
  } catch (error) {
    console.error('获取流量历史失败:', error)
    historyData.value = []
  } finally {
    loading.value = false
  }
}

// 格式化函数 - 因为数据已经是 GB 单位，所以直接格式化
const formatTraffic = (value) => {
  if (value === undefined || value === null || isNaN(value)) return '0.00 GB'
  return `${Number(value).toFixed(2)} GB`
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// 图表数据 - 直接使用数值，不需要额外转换
const chartData = computed(() => ({
  labels: historyData.value.map(d => formatTime(d.timestamp)),
  datasets: [
    {
      label: '上传流量',
      data: historyData.value.map(d => Number(d.upload_traffic)),
      borderColor: '#10B981',
      tension: 0.1
    },
    {
      label: '下载流量',
      data: historyData.value.map(d => Number(d.download_traffic)),
      borderColor: '#3B82F6',
      tension: 0.1
    },
    {
      label: '剩余流量',
      data: historyData.value.map(d => Number(d.remaining_traffic)),
      borderColor: '#8B5CF6',
      tension: 0.1
    }
  ]
}))

// 图表配置
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  plugins: {
    legend: {
      display: true
    }
  },
  scales: {
    x: {
      type: 'category',
      display: true
    },
    y: {
      type: 'linear',
      display: true,
      beginAtZero: true,
      title: {
        display: true,
        text: '流量 (GB)'
      }
    }
  }
}

// 处理用户选择
const handleUserSelect = () => {
  if (selectedUserId.value) {
    const selectedUser = users.value.find(u => u.id === selectedUserId.value)
    if (selectedUser) {
      userSearchQuery.value = selectedUser.username || selectedUser.email
      fetchTrafficHistory()
    }
  } else {
    userSearchQuery.value = ''
    historyData.value = []
  }
}

// 处理搜索输入
const handleSearch = () => {
  // 如果搜索框有内容，尝试匹配用户
  if (userSearchQuery.value) {
    const matchedUser = filteredUsers.value[0]
    if (matchedUser) {
      selectedUserId.value = matchedUser.id
      fetchTrafficHistory()
    }
  } else {
    // 如果搜索框清空，重置选择
    selectedUserId.value = ''
    historyData.value = []
  }
}

// 监听搜索查询变化
watch(userSearchQuery, (newVal) => {
  if (!newVal) {
    selectedUserId.value = ''
  }
})

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.form-select {
  @apply bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
         focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500;
}

.form-select:disabled {
  @apply bg-gray-100 dark:bg-gray-700 cursor-not-allowed;
}
</style> 
