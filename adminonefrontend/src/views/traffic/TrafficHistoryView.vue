<template>
  <div class="grid gap-6">
    <!-- 用户选择器 -->
    <CardBox>
      <div class="flex items-center space-x-4">
        <label class="text-gray-700 dark:text-gray-300">选择用户:</label>
        <select 
          v-model="selectedUserId"
          class="form-select rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-500"
          :disabled="loading"
          @change="fetchHistory"
        >
          <option value="">请选择用户</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.name }}
          </option>
        </select>
      </div>
    </CardBox>

    <!-- 错误提示 -->
    <CardBox v-if="error" class="bg-red-50 dark:bg-red-900/50">
      <div class="flex items-center text-red-700 dark:text-red-300">
        <BaseIcon :path="mdiAlert" class="w-6 h-6 mr-2"/>
        <span>{{ error }}</span>
      </div>
    </CardBox>

    <!-- 加载状态 -->
    <CardBox v-if="loading" class="flex justify-center items-center py-8">
      <BaseIcon :path="mdiLoading" class="w-8 h-8 animate-spin text-primary-500"/>
      <span class="ml-2">加载中...</span>
    </CardBox>

    <!-- 无数据提示 -->
    <CardBox v-else-if="!loading && historyData.length === 0" class="py-8">
      <div class="text-center text-gray-500">
        {{ selectedUserId ? '暂无流量记录' : '请选择用户查看流量历史' }}
      </div>
    </CardBox>

    <!-- 历史数据图表 -->
    <CardBox v-if="historyData.length > 0">
      <Line 
        :data="chartData" 
        :options="chartOptions"
        class="h-80"
      />
    </CardBox>

    <!-- 历史数据表格 -->
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
                剩余流量
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                时间
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="item in historyData" :key="item.timestamp">
              <td class="px-6 py-4 whitespace-nowrap">{{ item.container_id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.upload_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.download_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTraffic(item.remaining_traffic) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ formatTime(item.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </CardBox>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { mdiChartLine, mdiRefresh, mdiAlert, mdiLoading } from '@mdi/js'
import api from '@/services/api'

const users = ref([])
const selectedUserId = ref('')
const historyData = ref([])
const loading = ref(false)
const error = ref(null)

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await api.getUsers()
    if (response.success) {
      users.value = response.users
    }
  } catch (err) {
    error.value = '获取用户列表失败: ' + err.message
  }
}

// 获取历史数据
const fetchHistory = async () => {
  if (!selectedUserId.value) {
    error.value = '请选择用户'
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await api.getTrafficHistory(selectedUserId.value)
    if (response.success) {
      historyData.value = response.history_data
      if (historyData.value.length === 0) {
        error.value = '该用户暂无流量记录'
      }
    } else {
      throw new Error(response.message || '获取历史数据失败')
    }
  } catch (err) {
    error.value = err.message
    historyData.value = []
  } finally {
    loading.value = false
  }
}

// 图表数据
const chartData = computed(() => ({
  labels: historyData.value.map(d => formatTime(d.timestamp)),
  datasets: [
    {
      label: '上传流量',
      data: historyData.value.map(d => d.upload_traffic / 1024 / 1024),
      borderColor: '#10B981',
      tension: 0.1
    },
    {
      label: '下载流量',
      data: historyData.value.map(d => d.download_traffic / 1024 / 1024),
      borderColor: '#3B82F6',
      tension: 0.1
    },
    {
      label: '剩余流量',
      data: historyData.value.map(d => d.remaining_traffic / 1024 / 1024),
      borderColor: '#8B5CF6',
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

onMounted(() => {
  fetchUsers()
})
</script> 