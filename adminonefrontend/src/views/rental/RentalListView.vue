<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseDialog from '@/components/BaseDialog.vue'
import BaseDialogR from '@/components/BaseDialogR.vue'
import { 
  mdiPlus,
  mdiDelete,
  mdiRefresh,
  mdiPencil,
  mdiHistory,
  mdiBellRing,
  mdiCurrencyUsd,
  mdiInformation
} from '@mdi/js'
import api from '@/services/api'
import RentalRenewDialog from './RentalRenewDialog.vue'
import RentalCreateDialog from './RentalCreateDialog.vue'

// 添加 loading 状态
const loading = ref(false)

// 租赁数据
const rentals = ref([])
const currentPage = ref(1)
const itemsPerPage = 10

// 搜索条件
const searchQuery = ref({
  keyword: '',  // 统一的搜索关键字，用于序列号、用户名和邮箱
  status: ''    // 状态筛选
})

// 排序相关状态
const sortConfig = ref({
  key: 'id',        // 默认按ID排序
  order: 'desc'     // 默认降序
})

// 分页相关计算属性
const filteredRentals = computed(() => {
  let result = rentals.value

  // 搜索过滤
  if (searchQuery.value.keyword) {
    const keyword = searchQuery.value.keyword.toLowerCase()
    result = result.filter(rental => {
      // 检查序列号
      const serialMatch = rental.serial_code?.toLowerCase().includes(keyword)
      
      // 检查用户信息 - 使用 getUserDisplayName 函数
      const userInfo = getUserDisplayName(rental).toLowerCase()
      const userMatch = userInfo.includes(keyword)
      
      return serialMatch || userMatch
    })
  }

  // 状态过滤
  if (searchQuery.value.status) {
    result = result.filter(rental => rental.status === searchQuery.value.status)
  }

  // 排序
  result = [...result].sort((a, b) => {
    let compareResult = 0
    switch (sortConfig.value.key) {
      case 'id':
        compareResult = b.id - a.id // 默认按 ID 降序
        break
      case 'serial_code':
        compareResult = a.serial_code.localeCompare(b.serial_code)
        break
      case 'user_info':
        // 使用 getUserDisplayName 函数进行排序
        compareResult = getUserDisplayName(a).localeCompare(getUserDisplayName(b))
        break
      case 'start_date':
        compareResult = new Date(a.start_date) - new Date(b.start_date)
        break
      case 'end_date':
        compareResult = new Date(a.end_date) - new Date(b.end_date)
        break
      default:
        compareResult = 0
    }
    return sortConfig.value.order === 'desc' ? -compareResult : compareResult
  })

  return result
})

// 分页数据
const paginatedRentals = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredRentals.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => 
  Math.ceil(filteredRentals.value.length / itemsPerPage)
)

// 处理排序
const handleSort = (key) => {
  if (sortConfig.value.key === key) {
    sortConfig.value.order = sortConfig.value.order === 'asc' ? 'desc' : 'asc'
  } else {
    sortConfig.value.key = key
    sortConfig.value.order = 'asc'
  }
}

// 续费对话框状态
const showRenewDialog = ref(false)
const selectedRental = ref(null)

// 历史记录数据
const rentalHistory = ref([])
const showHistoryDialog = ref(false)

// 创建租赁对话框控制
const showCreateDialog = ref(false)

// 获取租赁列表
const fetchRentals = async () => {
  try {
    loading.value = true
    console.log('开始获取租赁列表...')
    
    const response = await api.getRentals()
    console.log('获取租赁列表响应:', response)
    
    if (response.success && Array.isArray(response.rentals)) {
      // 处理每个租赁对象，确保包含必要的用户信息
      rentals.value = response.rentals.map(rental => ({
        ...rental,
        user_info: rental.user_info || {
          email: rental.user_email || rental.email,
          username: rental.username
        }
      }))
      console.log('更新租赁列表成功，数量:', rentals.value.length)
    } else {
      console.warn('响应格式不正确:', response)
      throw new Error('获取租赁列表失败：数据格式不正确')
    }
  } catch (error) {
    console.error('获取租赁列表失败:', error)
    alert('获取租赁列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 删除租赁
const deleteRental = async (serialId) => {
  if (confirm('确定要删除该租赁记录吗？此操作将同时删除相关的容器和历史记录!')) {
    try {
      const response = await api.deleteRental(serialId);
      if (response.success) {
        alert('删除成功!');
        await fetchRentals();
      }
    } catch (error) {
      console.error('删除租赁失败:', error);
      alert('删除失败: ' + error.message);
    }
  }
};

// 发送到期通知
const sendExpiryNotifications = async () => {
  try {
    const response = await api.sendExpiryNotifications({ days_to_expiry: 7 });
    if (response.success) {
      alert('到期通知发送成功!');
    }
  } catch (error) {
    console.error('发送到期通知失败:', error);
    alert('发送通知失败: ' + error.message);
  }
};

// 检查租赁到期
const checkExpiry = async () => {
  try {
    const response = await api.checkRentalExpiry();
    if (response.success) {
      alert('已处理过期租赁!');
      await fetchRentals();
    }
  } catch (error) {
    console.error('检查租赁到期失败:', error);
    alert('检查到期失败: ' + error.message);
  }
};

// 处理续费结果
const handleRenewComplete = async (result) => {
  showRenewDialog.value = false
  selectedRental.value = null
  
  if (result.refresh) {
    // 刷新租赁列表
    await fetchRentals()
  }
}

// 打开续费对话框
const openRenewDialog = (rental) => {
  selectedRental.value = rental
  showRenewDialog.value = true
}

// 查看历史记录
const viewHistory = async (userId) => {
  try {
    const response = await api.getRentalHistory(userId)
    if (response.success) {
      rentalHistory.value = response.history
      showHistoryDialog.value = true
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    alert('获取历史记录失败: ' + error.message)
  }
}

// 处理续费
const handleRenew = async (renewalData) => {
  try {
    const response = await api.renewRental(renewalData)
    if (response.success) {
      alert('续费成功!')
      showRenewDialog.value = false
      await fetchRentals()
    }
  } catch (error) {
    console.error('续费失败:', error)
    alert('续费失败: ' + error.message)
  }
}

// 处理租赁创建成功
const handleRentalCreated = async () => {
  console.log('租赁创建成功，准备刷新列表...') // 添加日志
  showCreateDialog.value = false
  await fetchRentals() // 确保等待刷新完成
  console.log('租赁列表刷新完成') // 添加日志
}

// 初始化
onMounted(() => {
  fetchRentals()
})

const formatStatus = (status) => {
  const statusMap = {
    'active': '活跃',
    'expired': '已过期',
    'pending': '处理中'
  }
  return statusMap[status] || status
}

const formatPaymentStatus = (status) => {
  const statusMap = {
    'paid': '已支付',
    'unpaid': '未支付',
    'pending': '处理中',
    'failed': '支付失败'
  }
  return statusMap[status] || status
}

const formatContainerStatus = (status) => {
  const statusMap = {
    'running': '运行中',
    'stopped': '已停止',
    'pending': '启动中',
    'error': '错误'
  }
  return statusMap[status] || status
}

const formatServerStatus = (status) => {
  const statusMap = {
    'running': '运行中',
    'stopped': '已停止',
    'pending': '启动中',
    'error': '错误'
  }
  return statusMap[status] || status
}

// 添加日期格式化函数
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 添加时间格式化函数
const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

// 添加用户显示名称的处理函数
const getUserDisplayName = (rental) => {
  // 兼容多种可能的数据结构
  if (rental.user_info) {
    return rental.user_info.email || rental.user_info.username || '未知用户'
  }
  if (rental.user) {
    return rental.user.email || rental.user.username || '未知用户'
  }
  if (rental.user_email) {
    return rental.user_email
  }
  if (rental.username) {
    return rental.username
  }
  return '未知用户'
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox class="mb-6 dark:bg-gray-900">
        <!-- 标题和操作按钮 -->
        <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <h1 class="text-2xl font-bold dark:text-white">租赁管理</h1>
          <div class="flex flex-wrap gap-2">
            <BaseButton
              :icon="mdiPlus"
              color="success"
              @click="showCreateDialog = true"
              label="创建租赁"
              class="whitespace-nowrap"
            />
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              @click="fetchRentals"
              title="刷新"
              class="whitespace-nowrap"
            />
            <BaseButton
              :icon="mdiBellRing"
              color="warning"
              @click="sendExpiryNotifications"
              title="发送到期通知"
              class="whitespace-nowrap"
            />
          </div>
        </div>

        <!-- 搜索区域 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div class="form-group">
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">搜索</label>
            <input
              v-model="searchQuery.keyword"
              type="text"
              class="form-input dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700"
              placeholder="搜索序列号/用户名/邮箱"
            />
          </div>
          <div class="form-group">
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">状态</label>
            <select 
              v-model="searchQuery.status" 
              class="form-input dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700"
            >
              <option value="">全部</option>
              <option value="active">活跃</option>
              <option value="expired">已过期</option>
              <option value="pending">处理中</option>
            </select>
          </div>
        </div>

        <!-- 租赁列表表格 -->
        <div class="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th @click="handleSort('user_info')" 
                    class="group px-4 py-3 text-left cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 w-1/5"
                >
                  <div class="flex items-center space-x-1">
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">用户信息/序列号</span>
                    <span v-if="sortConfig.key === 'user_info'" class="text-gray-500 dark:text-gray-400">
                      {{ sortConfig.order === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th @click="handleSort('status')" 
                    class="group px-4 py-3 text-left cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 w-24"
                >
                  <div class="flex items-center space-x-1">
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">状态</span>
                    <span v-if="sortConfig.key === 'status'" class="text-gray-500 dark:text-gray-400">
                      {{ sortConfig.order === 'asc' ? '↑' : '↓' }}
                    </span>
                  </div>
                </th>
                <th class="px-4 py-3 text-left w-32">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">开始时间</span>
                </th>
                <th class="px-4 py-3 text-left w-32">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">到期时间</span>
                </th>
                <th class="px-4 py-3 text-left w-24">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">流量使用</span>
                </th>
                <th class="px-4 py-3 text-left w-28">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">运行状态</span>
                </th>
                <th class="px-4 py-3 text-left w-24">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">支付状态</span>
                </th>
                <th class="px-4 py-3 text-left w-28">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">操作</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
              <tr v-for="rental in paginatedRentals" 
                  :key="rental.id"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <td class="px-4 py-3">
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ getUserDisplayName(rental) }}
                    </span>
                    <span class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                      序列号: {{ rental.serial_code }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs font-medium px-2 py-1 rounded-full" :class="{
                    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': rental.status === 'active',
                    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': rental.status === 'expired',
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': rental.status === 'pending'
                  }">
                    {{ formatStatus(rental.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300 whitespace-nowrap">
                  <div class="flex flex-col">
                    <span>{{ formatDate(rental.start_date) }}</span>
                    <span class="text-gray-500">{{ formatTime(rental.start_date) }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300 whitespace-nowrap">
                  <div class="flex flex-col">
                    <span>{{ formatDate(rental.end_date) }}</span>
                    <span class="text-gray-500">{{ formatTime(rental.end_date) }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                  {{ rental.traffic_usage }}/{{ rental.traffic_limit }}GB
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-col space-y-0.5">
                    <div class="flex items-center space-x-0.5">
                      <span class="text-xs text-gray-500 dark:text-gray-400 min-w-[42px]">容器:</span>
                      <span class="text-xs font-medium px-1.5 py-0.5 rounded" :class="{
                        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': rental.container_status === 'running',
                        'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': rental.container_status === 'stopped',
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': rental.container_status === 'pending'
                      }">
                        {{ formatContainerStatus(rental.container_status) }}
                      </span>
                    </div>
                    <div class="flex items-center space-x-0.5">
                      <span class="text-xs text-gray-500 dark:text-gray-400 min-w-[42px]">服务器:</span>
                      <span class="text-xs font-medium px-1.5 py-0.5 rounded" :class="{
                        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': rental.server_status === 'running',
                        'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': rental.server_status === 'stopped',
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': rental.server_status === 'pending'
                      }">
                        {{ formatServerStatus(rental.server_status) }}
                      </span>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs font-medium px-2 py-1 rounded-full" :class="{
                    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': rental.payment_status === 'paid',
                    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': rental.payment_status === 'unpaid',
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': rental.payment_status === 'pending'
                  }">
                    {{ formatPaymentStatus(rental.payment_status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center space-x-1">
              <BaseButton
                      :icon="mdiPencil"
                color="info"
                      small
                      @click="openRenewDialog(rental)"
                      title="续费"
                    />
                    <BaseButton
                      :icon="mdiHistory"
                      color="success" 
                small
                      @click="viewHistory(rental.id)"
                      title="历史记录"
              />
              <BaseButton
                      :icon="mdiDelete"
                color="danger"
                small
                      @click="deleteRental(rental.id)"
                      title="删除"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="mt-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            共 {{ filteredRentals.length }} 条记录
          </div>
          <div class="flex items-center space-x-2">
            <BaseButton
              :disabled="currentPage === 1"
              @click="currentPage--"
              label="上一页"
              class="whitespace-nowrap"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
            />
            <span class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <BaseButton
              :disabled="currentPage >= totalPages"
              @click="currentPage++"
              label="下一页"
              class="whitespace-nowrap"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage >= totalPages }"
            />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>

  <!-- 对话框组件 -->
  <RentalCreateDialog
    :show="showCreateDialog"
    @close="showCreateDialog = false"
    @create="handleRentalCreated"
  />

  <RentalRenewDialog
    v-if="showRenewDialog"
    :show="showRenewDialog"
    :rental="selectedRental"
    @close="showRenewDialog = false"
    @renew="handleRenewComplete"
  />

  <BaseDialogR
    :show="showHistoryDialog"
    @close="showHistoryDialog = false"
  >
    <template #header>
      <div class="text-lg font-bold">租赁历史记录</div>
    </template>
    <template #default>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-4 py-2">开始日期</th>
              <th class="px-4 py-2">结束日期</th>
              <th class="px-4 py-2">状态</th>
              <th class="px-4 py-2">支付状态</th>
              <th class="px-4 py-2">流量使用</th>
              <th class="px-4 py-2">续费次数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="history in rentalHistory" :key="history.start_date">
              <td class="px-4 py-2">{{ new Date(history.start_date).toLocaleString() }}</td>
              <td class="px-4 py-2">{{ new Date(history.end_date).toLocaleString() }}</td>
              <td class="px-4 py-2">{{ history.status }}</td>
              <td class="px-4 py-2">{{ history.payment_status }}</td>
              <td class="px-4 py-2">{{ history.total_traffic }}GB</td>
              <td class="px-4 py-2">{{ history.renewal_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </BaseDialogR>
</template> 

<style scoped>
.form-group {
  @apply relative;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm 
         focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
         transition-colors duration-200
         dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300;
}

.form-input:disabled {
  @apply bg-gray-100 cursor-not-allowed
         dark:bg-gray-700 dark:text-gray-500;
}

/* 状态标签样式 */
.status-badge {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.status-badge-success {
  @apply bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200;
}

.status-badge-error {
  @apply bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200;
}

.status-badge-warning {
  @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200;
}

/* 表格悬停效果 */
.hover-row {
  @apply transition-colors duration-150 ease-in-out;
}

/* 按钮组样式 */
.button-group {
  @apply inline-flex rounded-md shadow-sm;
}

.button-group > :not([hidden]) ~ :not([hidden]) {
  @apply -ml-px;
}

/* 响应式优化 */
@media (max-width: 640px) {
  .overflow-x-auto {
    @apply -mx-4;
  }
  
  td, th {
    @apply whitespace-nowrap px-2;
  }
  
  .button-group {
    @apply flex-wrap gap-1;
  }
}
</style> 
