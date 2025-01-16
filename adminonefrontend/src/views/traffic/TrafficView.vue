<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiChartLine, 
  mdiRefresh, 
  mdiAlert,
  mdiDownload,
  mdiUpload,
  mdiServerNetwork,
  mdiAccountGroup,
  mdiChartTimelineVariant
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { Line } from 'vue-chartjs'
import api from '@/services/api'

// 数据状态
const trafficData = ref(null)
const realtimeData = ref([])
const selectedView = ref('realtime') // realtime, history, stats
const refreshInterval = ref(null)
const loading = ref(false)
const selectedUserId = ref(null)
const selectedServerId = ref(null)

// 图表配置
const chartData = computed(() => ({
  labels: realtimeData.value.map(d => new Date(d.timestamp).toLocaleTimeString()),
  datasets: [
    {
      label: '上传流量',
      data: realtimeData.value.map(d => d.upload_traffic / 1024 / 1024), // 转换为MB
      borderColor: '#10B981',
      fill: false
    },
    {
      label: '下载流量',
      data: realtimeData.value.map(d => d.download_traffic / 1024 / 1024),
      borderColor: '#3B82F6',
      fill: false
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
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

// 获取实时流量数据
const fetchRealtimeTraffic = async () => {
  try {
    loading.value = true
    const response = await api.getRealTimeTraffic()
    if (response.success) {
      realtimeData.value.push(...response.traffic_data)
      // 只保留最近30个数据点
      if (realtimeData.value.length > 30) {
        realtimeData.value = realtimeData.value.slice(-30)
      }
    }
  } catch (error) {
    console.error('获取实时流量数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取流量统计数据
const fetchTrafficStats = async () => {
  try {
    loading.value = true
    const params = {}
    if (selectedUserId.value) params.user_id = selectedUserId.value
    if (selectedServerId.value) params.server_id = selectedServerId.value
    
    const response = await api.getTrafficStats(params)
    if (response.success) {
      trafficData.value = response
    }
  } catch (error) {
    console.error('获取流量统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 检测超流量用户
const checkOverlimitUsers = async () => {
  try {
    const response = await api.detectOverlimitUsers()
    if (response.success && response.overlimit_users.length > 0) {
      // 显示警告通知
      alert(`检测到${response.overlimit_users.length}个用户超出流量限制！`)
    }
  } catch (error) {
    console.error('检测超流量用户失败:', error)
  }
}

// 组件挂载时启动定时刷新
onMounted(() => {
  fetchRealtimeTraffic()
  refreshInterval.value = setInterval(fetchRealtimeTraffic, 30000) // 每30秒刷新一次
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

// 手动刷新数据
const refreshData = () => {
  if (selectedView.value === 'realtime') {
    fetchRealtimeTraffic()
  } else {
    fetchTrafficStats()
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartLine" title="流量监控" main>
        <BaseButton
          :icon="mdiRefresh"
          :loading="loading"
          @click="refreshData"
          label="刷新"
          color="info"
        />
      </SectionTitleLineWithButton>

      <!-- 视图切换按钮组 -->
      <div class="mb-6">
        <div class="flex space-x-2">
          <BaseButton
            :icon="mdiChartTimelineVariant"
            :color="selectedView === 'realtime' ? 'success' : 'info'"
            @click="selectedView = 'realtime'"
            label="实时监控"
          />
          <BaseButton
            :icon="mdiAccountGroup"
            :color="selectedView === 'history' ? 'success' : 'info'"
            @click="selectedView = 'history'"
            label="历史记录"
          />
          <BaseButton
            :icon="mdiServerNetwork"
            :color="selectedView === 'stats' ? 'success' : 'info'"
            @click="selectedView = 'stats'"
            label="统计分析"
          />
        </div>
      </div>

      <!-- 实时监控视图 -->
      <div v-if="selectedView === 'realtime'">
        <!-- 流量概览卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <CardBox>
            <div class="flex items-center">
              <BaseIcon :path="mdiUpload" class="mr-4 text-emerald-500" size="48" />
              <div>
                <h3 class="text-lg font-semibold">上传流量</h3>
                <p class="text-2xl font-bold">
                  {{ 
                    realtimeData.value.length > 0 
                      ? (realtimeData.value[realtimeData.value.length - 1].upload_traffic / 1024 / 1024).toFixed(2) 
                      : '0.00'
                  }} MB
                </p>
              </div>
            </div>
          </CardBox>

          <CardBox>
            <div class="flex items-center">
              <BaseIcon :path="mdiDownload" class="mr-4 text-blue-500" size="48" />
              <div>
                <h3 class="text-lg font-semibold">下载流量</h3>
                <p class="text-2xl font-bold">
                  {{ 
                    realtimeData.value.length > 0 
                      ? (realtimeData.value[realtimeData.value.length - 1].download_traffic / 1024 / 1024).toFixed(2) 
                      : '0.00'
                  }} MB
                </p>
              </div>
            </div>
          </CardBox>

          <CardBox>
            <div class="flex items-center">
              <BaseIcon :path="mdiAlert" class="mr-4 text-red-500" size="48" />
              <div>
                <h3 class="text-lg font-semibold">异常检测</h3>
                <BaseButton
                  label="检测超限"
                  color="danger"
                  @click="checkOverlimitUsers"
                  small
                />
              </div>
            </div>
          </CardBox>
        </div>

        <!-- 流量图表 -->
        <CardBox class="mb-6">
          <div class="h-80">
            <Line
              v-if="realtimeData.value.length > 0"
              :data="chartData"
              :options="chartOptions"
            />
            <div v-else class="flex items-center justify-center h-full text-gray-500">
              暂无数据
            </div>
          </div>
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
                <tr v-for="data in realtimeData.value.slice().reverse()" :key="data.timestamp">
                  <td class="px-6 py-4 whitespace-nowrap">
                    {{ data.container_id }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    {{ (data.upload_traffic / 1024 / 1024).toFixed(2) }} MB
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    {{ (data.download_traffic / 1024 / 1024).toFixed(2) }} MB
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    {{ new Date(data.timestamp).toLocaleString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardBox>
      </div>

      <!-- 历史记录和统计分析视图的占位符 -->
      <div v-else>
        <CardBox>
          <div class="text-center py-12">
            <h3 class="text-lg font-medium text-gray-900">
              {{ selectedView === 'history' ? '历史记录' : '统计分析' }}功能开发中...
            </h3>
          </div>
        </CardBox>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.card-box-highlight {
  @apply transition-all duration-300 hover:shadow-lg;
}

.card-box-highlight:hover {
  transform: translateY(-2px);
}

/* 添加表格响应式滚动 */
.overflow-x-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.400') theme('colors.gray.100');
}

.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded hover:bg-gray-500;
}

/* 添加加载动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style> 