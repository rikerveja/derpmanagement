<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
  mdiCog
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseLevel from '@/components/BaseLevel.vue'

// 扩展状态管理
const containers = ref([])
const traffic = ref(null)
const alerts = ref([])
const rentalInfo = ref(null)
const servers = ref([])
const services = ref([])
const allContainers = ref([]) // 显示全部容器流量
const users = ref([])
const currentPage = ref(1)
const itemsPerPage = 10
const sortKey = ref('name')
const sortOrder = ref(1)

// 计算分页数据
const paginatedContainers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return allContainers.value.slice(start, end)
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return users.value.slice(start, end)
})

// 排序函数
const sortData = (data, key) => {
  if (sortKey.value === key) {
    sortOrder.value *= -1
  } else {
    sortKey.value = key
    sortOrder.value = 1
  }
  data.sort((a, b) => {
    if (a[key] < b[key]) return -1 * sortOrder.value
    if (a[key] > b[key]) return 1 * sortOrder.value
    return 0
  })
}

// 刷新数据
const refreshData = async () => {
  try {
    const [
      containersData,
      trafficData,
      alertsData,
      rentalData,
      serversData,
      servicesData,
      usersData
    ] = await Promise.all([
      api.getContainers(),
      api.getRealTimeTraffic(),
      api.getAlerts(),
      api.getRentalInfo(),
      api.getServers(),
      api.getServices(),
      api.get('/api/users')
    ])

    containers.value = containersData.containers
    traffic.value = trafficData.traffic
    alerts.value = alertsData.alerts
    rentalInfo.value = rentalData
    servers.value = serversData.servers
    services.value = servicesData.services
    users.value = usersData.users

    // 获取全部容器流量
    const allTrafficData = await api.get('/api/ha/container_traffic')
    allContainers.value = allTrafficData.containers

  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const viewRentalInfo = async (userId) => {
  const rentalInfo = await api.get(`/api/user/rental_info/${userId}`)
  console.log('租赁详情:', rentalInfo)
}

const viewRentalHistory = async (userId) => {
  const rentalHistory = await api.get(`/api/rental/history/${userId}`)
  console.log('租赁历史:', rentalHistory)
}

const downloadAcl = async (userId) => {
  window.open(`/api/user/download_acl/${userId}`, '_blank')
}

const replaceContainer = async (containerId) => {
  await api.post('/api/ha/replace_container', { containerId })
  console.log('容器替换成功')
}

const sendReminder = async (userId) => {
  await api.post('/api/notifications/send_reminder', { userId })
  console.log('续费通知已发送')
}

onMounted(() => {
  refreshData()
  const timer = setInterval(refreshData, 30000)
  onUnmounted(() => clearInterval(timer))
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
          @click="refreshData"
        />
      </SectionTitleLineWithButton>

      <!-- 系统状态卡片 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-4 mb-6">
        <!-- 容器状态 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-blue-500 p-3">
                <BaseIcon :path="mdiDocker" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">容器状态</p>
              <p class="text-lg font-semibold">{{ containers.length }} 个</p>
              <div class="text-sm text-gray-500">
                <span class="text-green-500">{{ containers.filter(c => c.status === 'running').length }} 运行</span> /
                <span class="text-gray-500">{{ containers.filter(c => c.status === 'stopped').length }} 停止</span> /
                <span class="text-red-500">{{ containers.filter(c => c.status === 'error').length }} 异常</span>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 服务器状态 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-purple-500 p-3">
                <BaseIcon :path="mdiServer" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">服务器状态</p>
              <p class="text-lg font-semibold">{{ servers.length }} 台</p>
              <div class="text-sm text-gray-500">
                <span class="text-green-500">{{ servers.filter(s => s.status === 'running').length }} 运行</span> /
                <span class="text-gray-500">{{ servers.filter(s => s.status === 'stopped').length }} 停止</span> /
                <span class="text-red-500">{{ servers.filter(s => s.status === 'error').length }} 异常</span>
              </div>
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
              <p class="text-lg font-semibold text-green-500">正常</p>
              <div class="text-sm text-gray-500 space-y-1">
                <div>邮件服务器：<span class="text-green-500 font-bold">正常</span></div>
                <div>Derp system：<span class="text-green-500 font-bold">正常</span></div>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 告警信息 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-red-500 p-3">
                <BaseIcon :path="mdiAlertCircle" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">告警信息</p>
              <p class="text-lg font-semibold">{{ alerts.length }} 个</p>
              <p class="text-sm text-gray-500">
                严重: {{ alerts.filter(a => a.level === 'critical').length }}
              </p>
            </div>
          </div>
        </CardBox>
      </div>

      <!-- 容器流量 -->
      <CardBox>
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-bold">容器流量</h3>
        </BaseLevel>
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th @click="sortData(allContainers, 'name')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">容器名称</th>
              <th @click="sortData(allContainers, 'serverIp')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">所在服务器IP</th>
              <th @click="sortData(allContainers, 'userEmail')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">用户邮箱</th>
              <th @click="sortData(allContainers, 'port')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">端口</th>
              <th @click="sortData(allContainers, 'stunPort')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">STUN端口</th>
              <th @click="sortData(allContainers, 'maxTraffic')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">最高流量</th>
              <th @click="sortData(allContainers, 'createdAt')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">创建时间</th>
              <th @click="sortData(allContainers, 'updatedAt')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">更新时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="container in paginatedContainers" :key="container.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ container.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.serverIp }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.userEmail }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.port }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.stunPort }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.maxTraffic }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.createdAt }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ container.updatedAt }}</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4">
          <BaseButton @click="currentPage--" :disabled="currentPage === 1" label="上一页" />
          <BaseButton @click="currentPage++" :disabled="currentPage * itemsPerPage >= allContainers.length" label="下一页" />
        </div>
      </CardBox>

      <!-- 分隔线 -->
      <div class="my-6"></div>

      <!-- 用户列表 -->
      <CardBox>
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-bold">用户列表</h3>
        </BaseLevel>
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th @click="sortData(users, 'username')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">用户名</th>
              <th @click="sortData(users, 'email')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">邮箱Email</th>
              <th @click="sortData(users, 'role')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">身份</th>
              <th @click="sortData(users, 'rentalExpiry')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">租约到期</th>
              <th @click="sortData(users, 'createdAt')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">创建时间</th>
              <th @click="sortData(users, 'lastLogin')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">最后登陆时间</th>
              <th @click="sortData(users, 'isVerified')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">是否验证</th>
              <th @click="sortData(users, 'verificationCode')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer">验证租赁码</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.role }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.rentalExpiry }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.createdAt }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.lastLogin }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.isVerified ? '是' : '否' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ user.verificationCode }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <BaseButton @click="viewRentalInfo(user.id)" label="查看租赁详情" />
                <BaseButton @click="viewRentalHistory(user.id)" label="租赁历史" />
                <BaseButton @click="downloadAcl(user.id)" label="下载ACL" />
                <BaseButton @click="sendReminder(user.id)" label="发送续费通知" />
              </td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4">
          <BaseButton @click="currentPage--" :disabled="currentPage === 1" label="上一页" />
          <BaseButton @click="currentPage++" :disabled="currentPage * itemsPerPage >= users.length" label="下一页" />
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
</style>