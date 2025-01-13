<script setup>
import { ref, onMounted } from 'vue'
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
const searchUserId = ref('')

// 获取历史记录
const fetchHistory = async () => {
  if (!searchUserId.value) {
    alert('请输入用户ID')
    return
  }

  try {
    loading.value = true
    const response = await api.getRentalHistory(searchUserId.value)
    if (response.success) {
      historyRecords.value = response.history
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    alert('获取历史记录失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

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
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox class="mb-6">
        <!-- 标题栏 -->
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold">租赁历史记录</h1>
          <div class="flex space-x-2">
            <div class="flex items-center">
              <input
                v-model="searchUserId"
                type="text"
                placeholder="输入用户ID"
                class="px-3 py-2 border rounded-md mr-2"
              />
              <BaseButton
                :icon="mdiMagnify"
                color="info"
                :loading="loading"
                @click="fetchHistory"
                label="查询"
              />
            </div>
            <BaseButton
              :icon="mdiRefresh"
              color="success"
              :loading="loading"
              @click="fetchHistory"
              title="刷新"
            />
          </div>
        </div>

        <!-- 历史记录列表 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">开始时间</th>
                <th class="px-4 py-3 text-left">结束时间</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">支付状态</th>
                <th class="px-4 py-3 text-left">流量使用</th>
                <th class="px-4 py-3 text-left">续费次数</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="record in historyRecords" :key="record.start_date">
                <td class="px-4 py-3">{{ new Date(record.start_date).toLocaleString() }}</td>
                <td class="px-4 py-3">{{ new Date(record.end_date).toLocaleString() }}</td>
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
                    <span class="font-medium">{{ record.total_traffic }}</span>
                    <span class="text-gray-500 ml-1">GB</span>
                  </div>
                </td>
                <td class="px-4 py-3">{{ record.renewal_count }}次</td>
              </tr>
              <tr v-if="historyRecords.length === 0">
                <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                  {{ searchUserId ? '未找到历史记录' : '请输入用户ID进行查询' }}
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

input[type="text"] {
  @apply focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style> 