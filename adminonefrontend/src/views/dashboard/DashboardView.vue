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
  mdiCog,
  mdiClockAlert,
  mdiCurrencyUsd,
  mdiKey
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

// 新增的响应式数据
const expiringUsers = ref([])
const expiringIn5Days = ref(0)
const expiringIn10Days = ref(0)
const totalIncome = ref(0)
const directIncome = ref(0)
const distributorIncome = ref(0)
const unpaidIncome = ref(0)
const totalSerials = ref(0)
const usedSerials = ref(0)
const unusedSerials = ref(0)
const deletedSerials = ref(0)

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
    console.log('开始刷新数据');
    const response = await api.getAllUsers();
    console.log('获取到的用户数据:', response); // 添加日志
    
    // 检查响应格式并正确提取数据
    if (response && Array.isArray(response)) {
      users.value = response;
    } else if (response && Array.isArray(response.data)) {
      users.value = response.data;
    } else if (response && response.users && Array.isArray(response.users)) {
      users.value = response.users;
    } else {
      console.error('用户数据格式不符合预期:', response);
      users.value = []; // 设置为空数组避免页面报错
    }

    try {
      // 获取到期用户数据
      const expiryData = await api.getExpiringUsers()
      expiringUsers.value = expiryData || []
      expiringIn5Days.value = (expiryData || []).filter(u => u.daysRemaining <= 5).length
      expiringIn10Days.value = (expiryData || []).filter(u => u.daysRemaining <= 10).length

      // 获取收入统计
      const incomeData = await api.getIncomeStats() || {}
      totalIncome.value = incomeData.total || 0
      directIncome.value = incomeData.direct || 0
      distributorIncome.value = incomeData.distributor || 0
      unpaidIncome.value = incomeData.unpaid || 0

      // 获取序列号统计
      const serialData = await api.getSerialStats() || {}
      totalSerials.value = serialData.total || 0
      usedSerials.value = serialData.used || 0
      unusedSerials.value = serialData.unused || 0
      deletedSerials.value = serialData.deleted || 0
    } catch (error) {
      console.error('获取额外统计数据失败:', error);
      // 不影响用户列表显示
    }

  } catch (error) {
    console.error('获取用户数据失败:', error);
    users.value = []; // 出错时设置为空数组
  }
}

const viewRentalInfo = async (userId) => {
  try {
    const rentalInfo = await api.getRentalInfo(userId)
    console.log('租赁详情:', rentalInfo)
  } catch (error) {
    console.error('获取租赁详情失败:', error)
  }
}

const viewRentalHistory = async (userId) => {
  try {
    const rentalHistory = await api.getRentalHistory(userId)
    console.log('租赁历史:', rentalHistory)
  } catch (error) {
    console.error('获取租赁历史失败:', error)
  }
}

const downloadAcl = async (userId) => {
  try {
    await api.downloadAcl(userId)
  } catch (error) {
    console.error('下载ACL失败:', error)
  }
}

const sendReminder = async (userId) => {
  try {
    await api.sendReminderNotification({ userId })
    console.log('续费通知已发送')
  } catch (error) {
    console.error('发送续费通知失败:', error)
  }
}

onMounted(() => {
  refreshData()
  // 可以暂时注释掉定时刷新，方便调试
  // const timer = setInterval(refreshData, 30000)
  // onUnmounted(() => clearInterval(timer))
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

        <!-- 用户统计 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-blue-500 p-3">
                <BaseIcon :path="mdiAccountMultiple" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">用户统计</p>
              <p class="text-lg font-semibold">{{ users.length }} 个</p>
              <div class="text-sm text-gray-500">
                <span>{{ users.filter(u => u.role === 'user').length }} 用户</span> /
                <span>{{ users.filter(u => u.role === 'admin').length }} 管理</span> /
                <span>{{ users.filter(u => u.role === 'distributor').length }} 分销</span>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 租约到期 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-yellow-500 p-3">
                <BaseIcon :path="mdiClockAlert" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">租约到期</p>
              <p class="text-lg font-semibold">{{ expiringUsers.length }} 个</p>
              <div class="text-sm text-gray-500">
                <span>{{ expiringIn5Days }} 剩余5日内</span> /
                <span>{{ expiringIn10Days }} 剩余10日内</span>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 收入统计 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-green-500 p-3">
                <BaseIcon :path="mdiCurrencyUsd" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">收入统计</p>
              <p class="text-lg font-semibold">¥ {{ totalIncome }}</p>
              <div class="text-sm text-gray-500">
                <span>{{ directIncome }} 直营</span> /
                <span>{{ distributorIncome }} 分销</span> /
                <span>{{ unpaidIncome }} 未结</span>
              </div>
            </div>
          </div>
        </CardBox>

        <!-- 序列号统计 -->
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-purple-500 p-3">
                <BaseIcon :path="mdiKey" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">序列号统计</p>
              <p class="text-lg font-semibold">{{ totalSerials }} 个</p>
              <div class="text-sm text-gray-500">
                <span>{{ usedSerials }} 已用</span> /
                <span>{{ unusedSerials }} 未用</span> /
                <span>{{ deletedSerials }} 已删</span>
              </div>
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
        <div class="mt-4 space-x-2">
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
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th @click="sortData(users, 'username')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">用户名</th>
                <th @click="sortData(users, 'email')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">Email</th>
                <th @click="sortData(users, 'role')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">角色</th>
                <th @click="sortData(users, 'rentalExpiry')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">租约到期</th>
                <th @click="sortData(users, 'last_login')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">登陆时间</th>
                <th @click="sortData(users, 'isVerified')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">验证</th>
                <th @click="sortData(users, 'verificationCode')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">租赁码</th>
                <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="user in paginatedUsers" :key="user.id">
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.username }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.email }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.role }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.rentalExpiry }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.last_login }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.isVerified ? '是' : '否' }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.verificationCode }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-center text-blue-600 dark:text-blue-400">
                  <span @click="viewRentalInfo(user.id)" class="cursor-pointer hover:underline">租赁详情</span> |
                  <span @click="viewRentalHistory(user.id)" class="cursor-pointer hover:underline">租赁历史</span> |
                  <span @click="downloadAcl(user.id)" class="cursor-pointer hover:underline">下载ACL</span> |
                  <span @click="sendReminder(user.id)" class="cursor-pointer hover:underline">续费通知</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="mt-4 space-x-2">
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

.overflow-x-auto {
  overflow-x: auto;
}
</style>
