<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseDialog from '@/components/BaseDialogR.vue'
import { 
  mdiPlus,
  mdiDelete,
  mdiRefresh,
  mdiPencil,
  mdiHistory,
  mdiBellRing,
  mdiCurrencyUsd
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
  serial_code: '',
  user_id: '',
  status: ''
})

// 续费对话框控制
const showRenewDialog = ref(false)
const currentRental = ref(null)

// 历史记录数据
const rentalHistory = ref([])
const showHistoryDialog = ref(false)

// 创建租赁对话框控制
const showCreateDialog = ref(false)

// 获取租赁列表
const fetchRentals = async () => {
  try {
    loading.value = true
    const response = await api.getRentals(searchQuery.value)
    if (response.success) {
      rentals.value = response.rentals
    }
  } catch (error) {
    console.error('获取租赁列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 创建租赁
const handleCreate = async (formData) => {
  try {
    loading.value = true
    const response = await api.createRental({
      serial_code: formData.serial_code,
      user_id: formData.user_id,
      traffic_limit: formData.traffic_limit || 0,
      container_config: formData.container_config
    })
    
    if (response.success) {
      alert('创建成功!')
      showCreateDialog.value = false
      await fetchRentals()
    }
  } catch (error) {
    console.error('创建租赁失败:', error)
    alert('创建失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 续费租赁
const renewRental = async () => {
  try {
    if (!renewalForm.value.serial_code || !renewalForm.value.renewal_amount || !renewalForm.value.renewal_period) {
      alert('请填写完整的续费信息')
      return
    }

    const response = await api.renewRental(renewalForm.value)
    if (response.success) {
      alert('续费成功!')
      await fetchRentals()
    }
  } catch (error) {
    console.error('续费失败:', error)
    alert('续费失败: ' + error.message)
  }
}

// 删除租赁
const deleteRental = async (serialId) => {
  if (confirm('确定要删除该租赁记录吗？此操作将同时删除相关的容器和历史记录!')) {
    try {
      const response = await api.deleteRental(serialId)
      if (response.success) {
        alert('删除成功!')
        await fetchRentals()
      }
    } catch (error) {
      console.error('删除租赁失败:', error)
      alert('删除失败: ' + error.message)
    }
  }
}

// 发送到期通知
const sendExpiryNotifications = async () => {
  try {
    const response = await api.sendExpiryNotifications({ days_to_expiry: 7 })
    if (response.success) {
      alert('到期通知发送成功!')
    }
  } catch (error) {
    console.error('发送到期通知失败:', error)
    alert('发送通知失败: ' + error.message)
  }
}

// 检查租赁到期
const checkExpiry = async () => {
  try {
    const response = await api.checkRentalExpiry()
    if (response.success) {
      alert('已处理过期租赁!')
      await fetchRentals()
    }
  } catch (error) {
    console.error('检查租赁到期失败:', error)
    alert('检查到期失败: ' + error.message)
  }
}

// 打开续费对话框
const openRenewDialog = (rental) => {
  currentRental.value = rental
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

// 初始化
onMounted(async () => {
  await fetchRentals()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox>
        <!-- 标题和操作按钮 -->
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold">租赁管理</h1>
          <div class="flex space-x-2">
            <BaseButton
              :icon="mdiPlus"
              color="success"
              @click="showCreateDialog = true"
              label="创建租赁"
            />
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              @click="fetchRentals"
              title="刷新"
            />
            <BaseButton
              :icon="mdiBellRing"
              color="warning"
              @click="sendExpiryNotifications"
              title="发送到期通知"
            />
          </div>
        </div>

        <!-- 搜索区域 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="form-group">
            <label>序列号</label>
            <input
              v-model="searchQuery.serial_code"
              type="text"
              class="form-input"
              placeholder="搜索序列号"
            />
          </div>
          <div class="form-group">
            <label>用户ID</label>
            <input
              v-model="searchQuery.user_id"
              type="text"
              class="form-input"
              placeholder="搜索用户ID"
            />
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="searchQuery.status" class="form-input">
              <option value="">全部</option>
              <option value="active">活跃</option>
              <option value="expired">已过期</option>
            </select>
          </div>
        </div>

        <!-- 租赁列表表格 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">序列号</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">开始日期</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">结束日期</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">流量使用</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">续费次数</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="rental in rentals" :key="rental.id">
                <td class="px-6 py-4">{{ rental.serial_code }}</td>
                <td class="px-6 py-4">{{ rental.user_id }}</td>
                <td class="px-6 py-4">
                  <span :class="{
                    'px-2 py-1 text-xs rounded-full': true,
                    'bg-green-100 text-green-800': rental.status === 'active',
                    'bg-red-100 text-red-800': rental.status === 'expired'
                  }">
                    {{ rental.status }}
                  </span>
                </td>
                <td class="px-6 py-4">{{ new Date(rental.start_date).toLocaleString() }}</td>
                <td class="px-6 py-4">{{ new Date(rental.end_date).toLocaleString() }}</td>
                <td class="px-6 py-4">{{ rental.traffic_usage }}GB / {{ rental.traffic_limit }}GB</td>
                <td class="px-6 py-4">{{ rental.renewal_count }}</td>
                <td class="px-6 py-4">
                  <div class="flex space-x-2">
                    <BaseButton
                      :icon="mdiCurrencyUsd"
                      color="success"
                      small
                      @click="openRenewDialog(rental)"
                      title="续费"
                    />
                    <BaseButton
                      :icon="mdiHistory"
                      color="info"
                      small
                      @click="viewHistory(rental.user_id)"
                      title="查看历史"
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
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>

  <!-- 对话框组件 -->
  <RentalRenewDialog
    :show="showRenewDialog"
    :rental="currentRental"
    @close="showRenewDialog = false"
    @renew="handleRenew"
  />

  <BaseDialog
    :show="showHistoryDialog"
    @close="showHistoryDialog = false"
    max-width="lg"
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
  </BaseDialog>

  <RentalCreateDialog
    v-if="showCreateDialog"
    :show="showCreateDialog"
    @close="showCreateDialog = false"
    @create="handleCreate"
  />
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

.form-input {
  @apply w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style> 
