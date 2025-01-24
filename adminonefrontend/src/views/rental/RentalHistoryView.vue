<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { 
  mdiHistory,
  mdiRefresh,
  mdiMagnify
} from '@mdi/js'
import api from '@/services/api'

// 历史记录数据
const historyRecords = ref([])
const loading = ref(false)
const users = ref([])
const loadingUsers = ref(false)
const userSearchQuery = ref('')
const selectedUserId = ref('')

// 过滤用户列表
const filteredUsers = computed(() => {
  const query = userSearchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username?.toLowerCase().includes(query) ||
    user.email?.toLowerCase().includes(query)
  )
})

// 获取用户列表
const fetchUsers = async () => {
  try {
    loadingUsers.value = true
    const response = await api.getAllUsers()
    if (response.success) {
      users.value = response.users
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loadingUsers.value = false
  }
}

// 获取历史记录
const fetchHistory = async () => {
  if (!selectedUserId.value) return

  try {
    loading.value = true
    const response = await api.getRentalHistory(selectedUserId.value)
    console.log('获取到的历史数据:', response) // 添加日志查看数据结构
    if (response.success) {
      historyRecords.value = response.history.map(record => ({
        ...record,
        // 使用 total_traffic 而不是 used_traffic
        used_traffic: typeof record.total_traffic === 'string' 
          ? parseFloat(record.total_traffic) 
          : record.total_traffic || 0,
        start_date: record.start_date,
        end_date: record.end_date,
        renewal_count: parseInt(record.renewal_count || 0)
      }))
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理用户选择
const handleUserSelect = () => {
  if (selectedUserId.value) {
    fetchHistory()
  } else {
    historyRecords.value = []
  }
}

// 处理搜索
const handleSearch = () => {
  if (userSearchQuery.value) {
    const matchedUser = filteredUsers.value[0]
    if (matchedUser) {
      selectedUserId.value = matchedUser.id
      fetchHistory()
    }
  } else {
    selectedUserId.value = ''
    historyRecords.value = []
  }
}

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers()
})

// 格式化状态
const formatStatus = (status) => {
  const statusMap = {
    'active': '使用中',
    'expired': '已到期',
    'pending': '待激活'
  }
  return statusMap[status] || status
}

// 格式化支付状态
const formatPaymentStatus = (status) => {
  const statusMap = {
    'paid': '已支付',
    'unpaid': '未支付',
    'pending': '处理中',
    'failed': '支付失败'
  }
  return statusMap[status] || status
}

// 添加日期格式化函数
const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 修改流量显示格式的函数
const formatTraffic = (traffic) => {
  if (!traffic) return '0.00'
  if (typeof traffic !== 'number') {
    traffic = parseFloat(traffic)
  }
  return traffic.toFixed(2)
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox>
        <!-- 添加用户搜索和选择部分 -->
        <div class="flex items-center space-x-4 mb-6">
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
          <BaseButton
            :icon="mdiRefresh"
            :loading="loading"
            @click="fetchHistory"
            :disabled="!selectedUserId"
          />
        </div>

        <!-- 历史记录表格 -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">开始日期</th>
                <th class="px-4 py-3 text-left">结束日期</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">支付状态</th>
                <th class="px-4 py-3 text-left">流量使用</th>
                <th class="px-4 py-3 text-left">续费次数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in historyRecords" :key="record.id">
                <td class="px-4 py-3">{{ formatDate(record.start_date) }}</td>
                <td class="px-4 py-3">{{ formatDate(record.end_date) }}</td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded-full text-xs': true,
                    'bg-green-100 text-green-800': record.status === 'active',
                    'bg-red-100 text-red-800': record.status === 'expired',
                    'bg-yellow-100 text-yellow-800': record.status === 'pending'
                  }">
                    {{ formatStatus(record.status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded-full text-xs': true,
                    'bg-green-100 text-green-800': record.payment_status === 'paid',
                    'bg-red-100 text-red-800': record.payment_status === 'unpaid',
                    'bg-yellow-100 text-yellow-800': record.payment_status === 'pending',
                    'bg-gray-100 text-gray-800': record.payment_status === 'failed'
                  }">
                    {{ formatPaymentStatus(record.payment_status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <span class="font-medium">{{ formatTraffic(record.total_traffic) }}</span>
                    <span class="text-gray-500 ml-1">GB</span>
                  </div>
                </td>
                <td class="px-4 py-3">{{ record.renewal_count }}次</td>
              </tr>
              <tr v-if="historyRecords.length === 0">
                <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                  {{ selectedUserId ? '未找到历史记录' : '请选择用户查看历史记录' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

.form-select {
  @apply bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 rounded-md shadow-sm 
         focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500;
}

.form-select:disabled {
  @apply bg-gray-100 dark:bg-gray-700 cursor-not-allowed;
}

input[type="text"] {
  @apply focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style> 
