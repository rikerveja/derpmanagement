<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiChartTimelineVariant, 
  mdiAccountMultiple, 
  mdiDocker, 
  mdiChartLine, 
  mdiEye,
  mdiServer,
  mdiAlertCircle,
  mdiCog,
  mdiClockAlert,
  mdiCurrencyUsd,
  mdiKey,
  mdiInformation,
  mdiHistory,
  mdiDownload,
  mdiBellRing,
  mdiRefresh,
  mdiClipboardList
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

// 核心状态数据
const stats = ref({
  containers: { total: 0, running: 0, stopped: 0, error: 0 },
  servers: { total: 0, running: 0, stopped: 0, error: 0 },
  users: { total: 0, active: 0, expired: 0 },
  alerts: { total: 0, critical: 0 },
  traffic: { used: 0, total: 0 },
  rentals: { total: 0, active: 0, expired: 0 },
  expiring: { in5days: 0, in10days: 0 },
  income: { total: 0, direct: 0, distributor: 0, unpaid: 0 },
  serials: { total: 0, used: 0, unused: 0, deleted: 0 }
})

const allContainers = ref([])
const users = ref([])
const serials = ref([])

// 分页设置
const currentPage = ref(1)
const itemsPerPage = 5 // 减少每页显示数量

// 当前选中的展示类型
const selectedView = ref('users')  // 默认显示用户概况

// 详细数据
const detailData = ref({
  traffic: {
    alerts: [],
    topUsers: [],
    monthlyStats: []
  },
  users: {
    newUsers: [],
    expiringUsers: [],
    activeStats: {}
  },
  finance: {
    recentTransactions: [],
    monthlyRevenue: [],
    distributorStats: {}
  }
})

const router = useRouter()

// 切换展示视图
const switchView = async (type) => {
  selectedView.value = type
  await fetchDetailData(type)
}

// 获取详细数据
const fetchDetailData = async (type) => {
  try {
    switch(type) {
      case 'traffic':
        const [trafficAlerts, trafficStats, overlimitUsers] = await Promise.all([
          api.getAlerts(),
          api.getTrafficStats(),
          api.getOverlimitUsers()
        ])
        
        detailData.value.traffic = {
          alerts: trafficAlerts?.data || [],
          topUsers: overlimitUsers?.data || [],
          monthlyStats: trafficStats?.data || {
            total: 0,
            avgPerUser: 0,
            overlimitUsers: 0
          }
        }
        break

      case 'users':
        const [newUsers, expiringUsers, activeStats] = await Promise.all([
          api.getAllUsers(),
          api.checkRentalExpiry(),
          api.getMonitoringStatus()
        ])
        
        detailData.value.users = {
          newUsers: (newUsers?.data || [])
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5),
          expiringUsers: expiringUsers?.data || [],
          activeStats: activeStats?.data?.users || {
            daily: 0,
            weekly: 0,
            monthly: 0
          }
        }
        break

      case 'finance':
        const [transactions, revenue, distributors] = await Promise.all([
          api.getIncomeStats(),
          api.getTrafficStats(),
          api.getAllUsers()
        ])
        
        detailData.value.finance = {
          recentTransactions: transactions?.data?.recent || [],
          monthlyRevenue: {
            current: revenue?.data?.currentMonth || 0,
            growth: revenue?.data?.growth || 0
          },
          distributorStats: {
            total: distributors?.data?.filter(u => u.role === 'distributor')?.length || 0,
            commission: transactions?.data?.distributorCommission || 0
          }
        }
        break
    }
  } catch (error) {
    console.error('获取详细数据失败:', error)
  }
}

// 获取仪表盘数据
const fetchStats = async () => {
  try {
    // 使用 axios 直接发起请求
    const response = await axios.get('/api/system/overview')
    console.log('Dashboard data response:', response)
    
    // 获取租赁数据来计算到期用户
    const rentalsResponse = await api.getRentals()
    if (rentalsResponse.success) {
      const now = new Date()
      const rentals = rentalsResponse.rentals
      
      // 计算5天内到期和5-10天内到期的用户数量
      const expiringStats = rentals.reduce((acc, rental) => {
        const daysRemaining = Math.ceil((new Date(rental.end_date) - now) / (1000 * 60 * 60 * 24))
        if (daysRemaining <= 5 && daysRemaining > 0) {
          acc.in5days++
        } else if (daysRemaining > 5 && daysRemaining <= 10) {
          acc.in10days++
        }
        return acc
      }, { in5days: 0, in10days: 0 })
      
      // 更新到期用户统计
      stats.value.expiring = expiringStats
      console.log('到期用户统计:', stats.value.expiring)
    }
    
    if (response.data && response.data.success) {
      const { data } = response.data
      console.log('Overview data:', data)
      
      // 直接更新状态数据
      stats.value.containers = data.containers
      stats.value.servers = data.servers
      stats.value.users = data.users
      stats.value.rentals = data.rentals
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

// 添加跳转方法
const goToRentalExpiry = () => {
  router.push('/rental/expiry')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStats()
  // 每60秒刷新一次数据
  const timer = setInterval(fetchStats, 60000)
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(timer)
  })
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiChartTimelineVariant"
        title="系统概览"
        main
      >
        <BaseButton
          :icon="mdiRefresh"
          color="info"
          @click="fetchStats"
          small
          title="刷新数据"
        />
      </SectionTitleLineWithButton>

      <!-- 核心指标卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- 服务器状态卡片 -->
        <router-link to="/servers/list" class="block">
          <CardBox class="cursor-pointer hover:shadow-lg transition-shadow duration-300">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-gray-500 dark:text-gray-400">服务器状态</div>
                <div class="flex items-center mt-2">
                  <BaseIcon :path="mdiServer" class="mr-2 text-blue-500" size="24" />
                  <div class="stats-number">{{ stats.servers.total }}</div>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-2 text-right">
                <div class="stat-item">
                  <span class="text-green-500 font-bold text-xl">{{ stats.servers.total }}</span>
                  <span class="text-sm text-gray-600">运行中</span>
                </div>
                <div class="stat-item">
                  <span class="text-red-500 font-bold text-xl">{{ stats.servers.error }}</span>
                  <span class="text-sm text-gray-600">异常</span>
                </div>
              </div>
            </div>
          </CardBox>
        </router-link>

        <!-- 容器状态卡片 -->
        <router-link to="/containers" class="block">
          <CardBox class="cursor-pointer hover:shadow-lg transition-shadow duration-300">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-gray-500 dark:text-gray-400">容器状态</div>
                <div class="flex items-center mt-2">
                  <BaseIcon :path="mdiDocker" class="mr-2 text-blue-500" size="24" />
                  <div class="stats-number">{{ stats.containers.total }}</div>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-2 text-right">
                <div class="stat-item">
                  <span class="text-green-500 font-bold text-xl">{{ stats.containers.running }}</span>
                  <span class="text-sm text-gray-600">运行中</span>
                </div>
                <div class="stat-item">
                  <span class="text-red-500 font-bold text-xl">{{ stats.containers.error }}</span>
                  <span class="text-sm text-gray-600">异常</span>
                </div>
              </div>
            </div>
          </CardBox>
        </router-link>

        <!-- 租赁状态卡片 -->
        <router-link to="/rental" class="block">
          <CardBox class="cursor-pointer hover:shadow-lg transition-shadow duration-300">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-gray-500 dark:text-gray-400">租赁状态</div>
                <div class="flex items-center mt-2">
                  <BaseIcon :path="mdiKey" class="mr-2 text-yellow-500" size="24" />
                  <div class="stats-number">{{ stats.rentals.total }}</div>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-2 text-right">
                <div class="stat-item">
                  <span class="text-green-500 font-bold text-xl">{{ stats.rentals.active }}</span>
                  <span class="text-sm text-gray-600">生效中</span>
                </div>
                <div class="stat-item">
                  <span class="text-red-500 font-bold text-xl">{{ stats.rentals.expired }}</span>
                  <span class="text-sm text-gray-600">已过期</span>
                </div>
              </div>
            </div>
          </CardBox>
        </router-link>
      </div>

      <!-- 第一行：用户和租约状态 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- 用户状态卡片 -->
        <CardBox 
          class="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
          @click="switchView('users')"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-purple-500 dark:bg-purple-400 p-3">
                <BaseIcon :path="mdiAccountMultiple" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-lg font-medium text-gray-800 dark:text-gray-200">用户状态</p>
              <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ stats.users.total }} 个</p>
              <div class="text-sm mt-2">
                <span class="bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300 px-2 py-1 rounded">
                  {{ stats.users.active }} 活跃
                </span>
                <span class="bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300 px-2 py-1 rounded ml-2">
                  {{ stats.users.expired }} 过期
                </span>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 租约到期卡片 -->
        <CardBox 
          class="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/30 dark:to-red-900/30 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
          @click="goToRentalExpiry"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-orange-500 p-3">
                <BaseIcon :path="mdiClockAlert" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-lg font-medium text-gray-800">租约到期</p>
              <p class="text-2xl font-bold text-red-600">{{ stats.expiring.in5days }} 个</p>
              <div class="text-sm mt-2">
                <span class="bg-orange-100 text-orange-800 px-2 py-1 rounded">
                  5天内: {{ stats.expiring.in5days }}
                </span>
                <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded ml-2">
                  10天内: {{ stats.expiring.in10days }}
                </span>
              </div>
            </div>
          </div>
        </CardBox>
      </div>

      <!-- 第二行：系统状态、流量统计和告警信息 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <!-- 系统运行状态卡片 -->
        <CardBox 
          class="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
          @click="switchView('traffic')"
        >
          <div class="flex flex-col">
            <div class="flex items-center mb-4">
            <div class="flex-shrink-0 p-4">
                <div class="rounded-full bg-blue-500 p-3">
                  <BaseIcon :path="mdiServer" class="text-white" />
                </div>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-300">系统运行状态</p>
                <p class="text-lg font-semibold">{{ stats.servers.total }} 台服务器</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 px-4">
              <div class="text-sm">
                <span class="text-green-500">{{ stats.servers.running }}</span> 服务器运行
              </div>
              <div class="text-sm">
                <span class="text-red-500">{{ stats.servers.error }}</span> 服务器异常
              </div>
              <div class="text-sm">
                <span class="text-green-500">{{ stats.containers.running }}</span> 容器运行
              </div>
              <div class="text-sm">
                <span class="text-red-500">{{ stats.containers.error }}</span> 容器异常
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 流量统计卡片 -->
        <CardBox 
          class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
          @click="switchView('traffic')"
        >
          <div class="flex flex-col">
            <div class="flex items-center mb-4">
            <div class="flex-shrink-0 p-4">
                <div class="rounded-full bg-blue-500 p-3">
                <BaseIcon :path="mdiChartLine" class="text-white" />
                </div>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600">流量统计</p>
                <p class="text-lg font-semibold">{{ stats.traffic.used }}GB / {{ stats.traffic.total }}GB</p>
              </div>
            </div>
            <div class="px-4">
              <div class="w-full bg-gray-200 rounded h-2 mb-2">
                <div class="bg-blue-600 h-2 rounded"
                     :style="{width: `${(stats.traffic.used / stats.traffic.total * 100)}%`}"
                ></div>
              </div>
              <div class="text-sm text-gray-500">
                使用率: {{ Math.round(stats.traffic.used / stats.traffic.total * 100) }}%
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 系统日志卡片 -->
        <CardBox 
          class="bg-gradient-to-r from-red-50 to-rose-50 dark:from-red-900/30 dark:to-rose-900/30 hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
          @click="switchView('traffic')"
        >
          <div class="flex flex-col">
            <div class="flex items-center mb-4">
              <div class="flex-shrink-0 p-4">
                <div class="rounded-full bg-red-500 p-3">
                  <BaseIcon :path="mdiBellRing" class="text-white" />
                </div>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-600">系统日志</p>
                <p class="text-lg font-semibold">{{ stats.alerts.total }} 条告警</p>
              </div>
            </div>
            <div class="px-4 space-y-2 max-h-32 overflow-y-auto">
              <div v-for="(alert, index) in detailData.traffic.alerts" 
                   :key="index"
                   class="text-sm p-2 rounded"
                   :class="alert.level === 'critical' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'">
                {{ alert.message }}
                <div class="text-xs opacity-75">{{ new Date(alert.time).toLocaleString() }}</div>
              </div>
            </div>
          </div>
        </CardBox>
      </div>

      <div class="mb-6">
        <BaseButtons>
          <BaseButton
            :color="selectedView === 'users' ? 'info' : 'white dark:gray'"
            :label="'用户概况'"
            :icon="mdiAccountMultiple"
            @click="switchView('users')"
          />
          <BaseButton
            :color="selectedView === 'traffic' ? 'info' : 'white dark:gray'"
            :label="'流量概况'"
            :icon="mdiChartLine"
            @click="switchView('traffic')"
          />
          <BaseButton 
            :color="selectedView === 'finance' ? 'info' : 'white dark:gray'"
            :label="'财务概况'"
            :icon="mdiCurrencyUsd"
            @click="switchView('finance')"
          />
        </BaseButtons>
      </div>

      <CardBox>
        <div v-if="selectedView === 'traffic'">
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-bold dark:text-white">流量警报概况</h3>
          </BaseLevel>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="p-4 bg-red-50 dark:bg-red-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">异常流量警报</h4>
              <div v-for="alert in detailData.traffic.alerts" :key="alert.id"
                   class="mb-2 p-2 bg-white rounded shadow">
                <p class="text-sm">{{ alert.message }}</p>
                <p class="text-xs text-gray-500">{{ new Date(alert.time).toLocaleString() }}</p>
              </div>
            </div>
            
            <!-- 高流量用户 -->
            <div class="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">高流量用户</h4>
              <div v-for="user in detailData.traffic.topUsers" :key="user.id"
                   class="mb-2 p-2 bg-white rounded shadow">
                <p class="text-sm">{{ user.username }}</p>
                <div class="w-full bg-gray-200 rounded h-2">
                  <div class="bg-blue-600 h-2 rounded"
                       :style="{width: `${(user.used_traffic / user.max_traffic * 100)}%`}"
                  ></div>
                </div>
              </div>
            </div>
            
            <!-- 月度统计 -->
            <div class="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">月度流量统计</h4>
              <div class="space-y-2">
                <p class="text-sm">总流量: {{ detailData.traffic.monthlyStats.total }}GB</p>
                <p class="text-sm">平均每用户: {{ detailData.traffic.monthlyStats.avgPerUser }}GB</p>
                <p class="text-sm">超限用户数: {{ detailData.traffic.monthlyStats.overlimitUsers }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户概况 -->
        <div v-if="selectedView === 'users'">
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-bold dark:text-white">用户概况</h3>
          </BaseLevel>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- 新增用户 -->
            <div class="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <h4 class="font-semibold mb-2 dark:text-gray-200">新增用户</h4>
              <div v-for="user in detailData.users.newUsers" :key="user.id"
                   class="mb-2 p-2 bg-white dark:bg-gray-800 rounded shadow">
                <p class="text-sm dark:text-gray-300">{{ user.username }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">注册时间: {{ new Date(user.created_at).toLocaleString() }}</p>
                </div>
                </div>
            
            <!-- 即将到期 -->
            <div class="p-4 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg cursor-pointer" 
                 @click="goToRentalExpiry">
              <h4 class="font-semibold mb-2 dark:text-gray-200 flex items-center">
                <BaseIcon :path="mdiClockAlert" class="mr-2" />
                即将到期用户
              </h4>
              <div class="space-y-2">
                <p class="text-sm dark:text-gray-300">
                  5天内到期: {{ stats.expiring.in5days }} 个
                </p>
                <p class="text-sm dark:text-gray-300">
                  5-10天内到期: {{ stats.expiring.in10days }} 个
                </p>
              </div>
              <div class="mt-2 text-xs text-blue-600 dark:text-blue-400">
                点击查看详情 →
              </div>
            </div>
            
            <!-- 活跃度统计 -->
            <div class="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <h4 class="font-semibold mb-2 dark:text-gray-200">用户活跃度</h4>
              <div class="space-y-2">
                <p class="text-sm dark:text-gray-300">日活跃: {{ detailData.users.activeStats.daily }}</p>
                <p class="text-sm dark:text-gray-300">周活跃: {{ detailData.users.activeStats.weekly }}</p>
                <p class="text-sm dark:text-gray-300">月活跃: {{ detailData.users.activeStats.monthly }}</p>
              </div>
            </div>
          </div>
      </div>

        <!-- 财务概况 -->
        <div v-if="selectedView === 'finance'">
        <BaseLevel class="mb-4">
            <h3 class="text-lg font-bold dark:text-white">财务概况</h3>
        </BaseLevel>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- 最近交易 -->
            <div class="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">最近交易</h4>
              <div v-for="transaction in detailData.finance.recentTransactions" :key="transaction.id"
                   class="mb-2 p-2 bg-white rounded shadow">
                <p class="text-sm">¥{{ transaction.amount }}</p>
                <p class="text-xs text-gray-500">{{ new Date(transaction.time).toLocaleString() }}</p>
                    </div>
                  </div>
            
            <!-- 月度收入 -->
            <div class="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">月度收入</h4>
              <div class="space-y-2">
                <p class="text-sm">本月收入: ¥{{ detailData.finance.monthlyRevenue.current }}</p>
                <p class="text-sm">环比: {{ detailData.finance.monthlyRevenue.growth }}%</p>
              </div>
        </div>
            
            <!-- 分销商统计 -->
            <div class="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
              <h4 class="font-semibold mb-2">分销商统计</h4>
              <div class="space-y-2">
                <p class="text-sm">分销商数量: {{ detailData.finance.distributorStats.total }}</p>
                <p class="text-sm">本月佣金: ¥{{ detailData.finance.distributorStats.commission }}</p>
              </div>
            </div>
          </div>
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

/* 添加一些过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.overflow-x-auto {
  overflow-x: auto;
}

/* 添加工具提示的样式 */
button {
  position: relative;
}

button:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 10;
}

/* 添加渐变背景和阴影效果 */
.card-box-highlight {
  @apply shadow-lg transition-all duration-300;
}

.card-box-highlight:hover {
  @apply shadow-xl transform -translate-y-1;
}

/* 添加醒目的数字样式 */
.stats-number {
  @apply text-4xl font-bold text-gray-800 dark:text-white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-item {
  @apply flex flex-col items-end;
}

.stat-item span:first-child {
  @apply transition-all duration-300;
}

.stat-item:hover span:first-child {
  @apply transform scale-110;
}

/* 暗色模式适配 */
:deep(.dark) .stats-number {
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
</style> 
