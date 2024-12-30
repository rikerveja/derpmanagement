<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiChartTimelineVariant, mdiAccountMultiple, mdiDocker, mdiChartLine, mdiEye, mdiServer, mdiAlertCircle } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import { Line, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'

// 注册 Chart.js 组件
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

// 添加更多状态管理
const containers = ref([])
const traffic = ref(null)
const alerts = ref([])
const rentalInfo = ref(null)
const serverHealth = ref(null)
const systemStatus = ref(null)

// 添加定时刷新功能
let refreshTimer = null

const startAutoRefresh = () => {
  refreshTimer = setInterval(async () => {
    await fetchDashboardData()
  }, 30000) // 每30秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
}

// 添加图表数据
const containerChartData = ref({
  labels: ['运行中', '已停止', '异常'],
  datasets: [{
    backgroundColor: ['#10B981', '#6B7280', '#EF4444'],
    data: [0, 0, 0]
  }]
})

// 修改流量图表数据结构
const serverTrafficChartData = ref({
  labels: [],
  datasets: [] // 动态生成每个服务器的数据集
})

const containerTrafficChartData = ref({
  labels: [],
  datasets: [] // 动态生成每个容器的数据集
})

// 更新图表数据的函数
const updateChartData = () => {
  // 更新容器状态图表
  const running = containers.value.filter(c => c.status === 'running').length
  const stopped = containers.value.filter(c => c.status === 'stopped').length
  const error = containers.value.filter(c => c.status === 'error').length
  containerChartData.value.datasets[0].data = [running, stopped, error]

  // 更新服务器流量图表
  const now = new Date()
  serverTrafficChartData.value.labels.push(now.toLocaleTimeString())
  
  // 为每个服务器创建或更新数据集
  servers.value.forEach((server, index) => {
    if (!serverTrafficChartData.value.datasets[index]) {
      serverTrafficChartData.value.datasets[index] = {
        label: `${server.name} 流量`,
        borderColor: getServerColor(index), // 生成不同的颜色
        data: [],
        fill: false
      }
    }
    serverTrafficChartData.value.datasets[index].data.push(server.traffic?.total || 0)
  })

  // 更新容器流量图表
  containerTrafficChartData.value.labels.push(now.toLocaleTimeString())
  
  // 获取流量最高的前5个容器
  const topContainers = containers.value
    .sort((a, b) => (b.traffic?.total || 0) - (a.traffic?.total || 0))
    .slice(0, 5)

  // 更新容器流量数据集
  topContainers.forEach((container, index) => {
    if (!containerTrafficChartData.value.datasets[index]) {
      containerTrafficChartData.value.datasets[index] = {
        label: `${container.name}`,
        borderColor: getContainerColor(index),
        data: [],
        fill: false
      }
    }
    containerTrafficChartData.value.datasets[index].data.push(container.traffic?.total || 0)
  })

  // 保持最近 10 个数据点
  if (serverTrafficChartData.value.labels.length > 10) {
    serverTrafficChartData.value.labels.shift()
    serverTrafficChartData.value.datasets.forEach(dataset => dataset.data.shift())
    containerTrafficChartData.value.labels.shift()
    containerTrafficChartData.value.datasets.forEach(dataset => dataset.data.shift())
  }
}

// 生成颜色函数
const getServerColor = (index) => {
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return colors[index % colors.length]
}

const getContainerColor = (index) => {
  const colors = ['#60A5FA', '#34D399', '#FBBF24', '#F87171', '#A78BFA']
  return colors[index % colors.length]
}

// 添加服务器和用户状态管理
const servers = ref([])
const users = ref([])

// 添加分销相关的状态管理
const distributors = ref([])
const distributorStats = ref({
  totalSales: 0,
  monthSales: 0,
  activeDistributors: 0,
  topPerformers: []
})

// 添加分销业绩图表数据
const salesChartData = ref({
  labels: [], // 最近12个月
  datasets: [
    {
      label: '月度销售额',
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      data: [],
      fill: true
    }
  ]
})

// 统一获取数据的函数
const fetchDashboardData = async () => {
  try {
    const [
      containersData, 
      trafficData, 
      alertsData, 
      rentalData, 
      serversData, 
      usersData, 
      statusData,
      distributorsData,  // 新增分销数据获取
      salesData          // 新增销售数据获取
    ] = await Promise.all([
      api.getContainers(),
      api.getRealTimeTraffic(),
      api.getAlerts(),
      api.getRentalInfo(),
      api.get('/api/servers'),
      api.get('/api/users'),
      api.get('/api/monitoring'),
      api.get('/api/distributors'),
      api.get('/api/sales/statistics')
    ])

    containers.value = containersData.containers
    traffic.value = trafficData.traffic
    alerts.value = alertsData.alerts
    rentalInfo.value = rentalData
    servers.value = serversData.servers
    users.value = usersData.users
    systemStatus.value = statusData

    // 更新分销相关数据
    distributors.value = distributorsData.distributors
    distributorStats.value = salesData.statistics
    updateSalesChart(salesData.monthlyData)

    updateChartData()
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

// 更新销售图表数据
const updateSalesChart = (monthlyData) => {
  salesChartData.value.labels = monthlyData.map(item => item.month)
  salesChartData.value.datasets[0].data = monthlyData.map(item => item.amount)
}

// 添加新的函数处理续租
const handleRenewal = async () => {
  try {
    await api.post('/api/rental/renew', {
      rental_id: rentalInfo.value?.rental_id,
      // 可以添加其他续租参数
    })
    // 续租成功后刷新数据
    await fetchDashboardData()
  } catch (error) {
    console.error('续租失败:', error)
    // 这里可以添加错误提示
  }
}

// 添加处理告警的函数
const handleAlert = async (alertId) => {
  try {
    await api.post(`/api/alerts/handle/${alertId}`)
    // 处理成功后刷新告警列表
    await fetchDashboardData()
  } catch (error) {
    console.error('处理告警失败:', error)
    // 这里可以添加错误提示
  }
}

onMounted(async () => {
  await fetchDashboardData()
  startAutoRefresh()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="系统概览" main>
        <BaseButton
          :icon="mdiEye"
          color="info"
          outline
          label="刷新"
          @click="fetchDashboardData"
        />
      </SectionTitleLineWithButton>

      <!-- 核心指标卡片 - 第一行 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-4 mb-6">
        <!-- 服务器数量 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-purple-500 p-3">
                <BaseIcon :path="mdiServer" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">服务器数量</p>
              <p class="text-lg font-semibold">{{ servers.length }}</p>
              <p class="text-sm text-gray-500">
                在线: {{ servers.filter(s => s.status === 'online').length }}
              </p>
            </div>
          </div>
        </CardBox>

        <!-- 用户总数 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-indigo-500 p-3">
                <BaseIcon :path="mdiAccountMultiple" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">用户总数</p>
              <p class="text-lg font-semibold">{{ users.length }}</p>
              <p class="text-sm text-gray-500">
                活跃: {{ users.filter(u => u.status === 'active').length }}
              </p>
            </div>
          </div>
        </CardBox>

        <!-- 告警状态 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-red-500 p-3">
                <BaseIcon :path="mdiAlertCircle" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">告警数量</p>
              <p class="text-lg font-semibold">{{ alerts.length }}</p>
              <p class="text-sm text-gray-500">
                严重: {{ alerts.filter(a => a.level === 'critical').length }}
              </p>
            </div>
          </div>
        </CardBox>

        <!-- 系统状态 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-green-500 p-3">
                <BaseIcon :path="mdiChartLine" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">系统状态</p>
              <p class="text-lg font-semibold">{{ systemStatus?.status || '正常' }}</p>
              <p class="text-sm text-gray-500">
                运行时间: {{ systemStatus?.uptime || '未知' }}
              </p>
            </div>
          </div>
        </CardBox>
      </div>

      <!-- 图表和详细信息 - 第二行 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-6">
        <!-- 容器状态卡片 -->
        <CardBox>
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-medium">容器状态</h3>
            <p class="text-sm text-gray-500">总数: {{ containers.length }}</p>
          </BaseLevel>
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="text-center">
                  <p class="text-sm font-medium text-gray-600">运行中</p>
                  <p class="text-lg font-semibold text-green-600">
                    {{ containers.filter(c => c.status === 'running').length }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm font-medium text-gray-600">已停止</p>
                  <p class="text-lg font-semibold text-gray-600">
                    {{ containers.filter(c => c.status === 'stopped').length }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm font-medium text-gray-600">异常</p>
                  <p class="text-lg font-semibold text-red-600">
                    {{ containers.filter(c => c.status === 'error').length }}
                  </p>
                </div>
              </div>
            </div>
            <div class="w-48 h-48">
              <Doughnut
                :data="containerChartData"
                :options="{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: true,
                      position: 'bottom'
                    }
                  }
                }"
              />
            </div>
          </div>
        </CardBox>

        <!-- 服务器流量监控卡片 -->
        <CardBox>
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-medium">服务器流量监控</h3>
            <div class="text-sm text-gray-500">
              总流量: {{ servers.reduce((sum, server) => sum + (server.traffic?.total || 0), 0).toFixed(2) }} MB/s
            </div>
          </BaseLevel>
          <div class="h-48">
            <Line
              :data="serverTrafficChartData"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom'
                  },
                  tooltip: {
                    mode: 'index',
                    intersect: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'MB/s'
                    }
                  }
                }
              }"
            />
          </div>
        </CardBox>
      </div>

      <!-- 容器流量监控 - 新增第三行 -->
      <CardBox class="mb-6">
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">容器流量监控 (Top 5)</h3>
          <div class="text-sm text-gray-500">
            活跃容器: {{ containers.filter(c => c.status === 'running').length }}
          </div>
        </BaseLevel>
        <div class="h-48">
          <Line
            :data="containerTrafficChartData"
            :options="{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'bottom'
                },
                tooltip: {
                  mode: 'index',
                  intersect: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'MB/s'
                  }
                }
              }
            }"
          />
        </div>
        <!-- 添加容器流量详情表格 -->
        <div class="mt-4 overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">容器名称</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">所属服务器</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">入站流量</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">出站流量</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">总流量</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="container in containers
                .sort((a, b) => (b.traffic?.total || 0) - (a.traffic?.total || 0))
                .slice(0, 5)" 
                :key="container.id">
                <td class="px-6 py-4 whitespace-nowrap">{{ container.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ container.server_name }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ container.traffic?.in || 0 }} MB/s</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ container.traffic?.out || 0 }} MB/s</td>
                <td class="px-6 py-4 whitespace-nowrap font-medium" 
                    :class="{'text-green-600': container.traffic?.total > 0}">
                  {{ container.traffic?.total || 0 }} MB/s
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>

      <!-- 用户管理概览 - 第三行 -->
      <CardBox class="mb-6">
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">用户管理概览</h3>
          <BaseButton 
            :icon="mdiEye" 
            to="/users" 
            color="info" 
            outline 
            label="查看全部" 
          />
        </BaseLevel>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">容器数</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最近登录</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in users.slice(0, 5)" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap">{{ user.username }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                        :class="{
                          'bg-green-100 text-green-800': user.status === 'active',
                          'bg-gray-100 text-gray-800': user.status === 'inactive'
                        }">
                    {{ user.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">{{ user.containers_count || 0 }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ user.last_login || '从未登录' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>

      <!-- 分销业绩概览 - 在用户管理概览之前添加 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-6">
        <!-- 分销业绩统计卡片 -->
        <CardBox>
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-medium">分销业绩统计</h3>
          </BaseLevel>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="bg-blue-50 rounded-lg p-4">
              <p class="text-sm text-blue-600 font-medium">本月销售额</p>
              <p class="text-2xl font-bold text-blue-700">¥{{ distributorStats.monthSales.toLocaleString() }}</p>
              <p class="text-sm text-blue-500">活跃分销商: {{ distributorStats.activeDistributors }}</p>
            </div>
            <div class="bg-green-50 rounded-lg p-4">
              <p class="text-sm text-green-600 font-medium">累计销售额</p>
              <p class="text-2xl font-bold text-green-700">¥{{ distributorStats.totalSales.toLocaleString() }}</p>
              <p class="text-sm text-green-500">总分销商: {{ distributors.length }}</p>
            </div>
          </div>
          <div class="h-48">
            <Line
              :data="salesChartData"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => `销售额: ¥${context.raw.toLocaleString()}`
                    }
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: '销售额 (¥)'
                    }
                  }
                }
              }"
            />
          </div>
        </CardBox>

        <!-- 顶级分销商榜单 -->
        <CardBox>
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-medium">顶级分销商</h3>
            <BaseButton 
              :icon="mdiEye" 
              to="/distributors" 
              color="info" 
              outline 
              label="查看全部" 
            />
          </BaseLevel>
          <div class="space-y-4">
            <div v-for="(distributor, index) in distributorStats.topPerformers" 
                 :key="distributor.id"
                 class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-4">
                <div :class="`w-8 h-8 flex items-center justify-center rounded-full 
                  ${index === 0 ? 'bg-yellow-400' : 
                    index === 1 ? 'bg-gray-300' : 
                    index === 2 ? 'bg-yellow-600' : 'bg-gray-200'} 
                  text-white font-bold`">
                  {{ index + 1 }}
                </div>
                <div>
                  <p class="font-medium">{{ distributor.name }}</p>
                  <p class="text-sm text-gray-500">注册时间: {{ distributor.joinDate }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="font-bold text-blue-600">¥{{ distributor.monthSales.toLocaleString() }}</p>
                <p class="text-sm text-gray-500">本月销售额</p>
              </div>
            </div>
          </div>
        </CardBox>
      </div>

      <!-- 分销商详细列表 -->
      <CardBox class="mb-6">
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">分销商管理</h3>
          <BaseButton 
            :icon="mdiEye" 
            to="/distributors" 
            color="info" 
            outline 
            label="管理分销商" 
          />
        </BaseLevel>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分销商</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">本月销售额</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">累计销售额</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">客户数</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最近活动</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="distributor in distributors.slice(0, 5)" :key="distributor.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ distributor.name }}</div>
                      <div class="text-sm text-gray-500">{{ distributor.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                        :class="{
                          'bg-green-100 text-green-800': distributor.status === 'active',
                          'bg-gray-100 text-gray-800': distributor.status === 'inactive'
                        }">
                    {{ distributor.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ¥{{ distributor.monthSales.toLocaleString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ¥{{ distributor.totalSales.toLocaleString() }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ distributor.customerCount }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ distributor.lastActivity }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>

      <!-- 最近告警 - 第四行 -->
      <CardBox>
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">最近告警</h3>
          <BaseButton 
            v-if="alerts.length"
            :icon="mdiEye" 
            to="/alerts" 
            color="info" 
            outline 
            label="查看全部" 
          />
        </BaseLevel>
        <div v-if="alerts.length" class="space-y-4">
          <div v-for="alert in alerts.slice(0, 5)" 
               :key="alert.alert_id" 
               class="p-4 border-b"
               :class="{
                 'bg-red-50': alert.level === 'critical',
                 'bg-yellow-50': alert.level === 'warning'
               }">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium">{{ alert.message }}</p>
                <p class="text-sm text-gray-500">{{ alert.timestamp }}</p>
              </div>
              <BaseButton
                size="small"
                color="danger"
                @click="handleAlert(alert.alert_id)"
                label="处理"
              />
            </div>
          </div>
        </div>
        <div v-else class="text-center text-gray-500 py-4">
          暂无告警信息
        </div>
      </CardBox>

      <!-- 租赁信息放在最后 -->
      <CardBox class="mt-6" v-if="rentalInfo">
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">租赁信息</h3>
        </BaseLevel>
        <div class="space-y-2">
          <p>状态: {{ rentalInfo.rental_status }}</p>
          <p>到期时间: {{ rentalInfo.rental_expiry }}</p>
          <BaseButton
            v-if="rentalInfo.rental_status === 'active'"
            color="success"
            label="续租"
            @click="handleRenewal"
          />
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 200px;
}
</style> 
