<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import BaseDialogR from '@/components/BaseDialogR.vue'
import BaseButton from '@/components/BaseButton.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  rental: Object
})

const emit = defineEmits(['close'])
const rentalHistory = ref([])
const loading = ref(false)
const searchQuery = ref('')

// 过滤后的历史记录
const filteredHistory = computed(() => {
  if (!searchQuery.value) return rentalHistory.value
  const query = searchQuery.value.toLowerCase()
  return rentalHistory.value.filter(record => 
    record.serial_code.toLowerCase().includes(query)
  )
})

const formatDate = (date) => {
  return date ? new Date(date).toLocaleString() : '-'
}

// 获取租赁历史记录
const fetchRentalHistory = async () => {
  if (!props.rental?.user_id) return
  
  try {
    loading.value = true
    const response = await api.getSerials()
    console.log('序列号列表响应:', response)

    if (response && response.serial_numbers) {
      // 过滤出当前用户的序列号
      const userSerials = response.serial_numbers.filter(
        serial => serial.user_id === props.rental.user_id
      )
      
      console.log('用户序列号:', userSerials)
      
      // 按创建时间排序
      userSerials.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      
      // 转换为历史记录格式
      rentalHistory.value = userSerials.map((serial, index) => ({
        id: serial.id,
        serial_code: serial.serial_code,
        operation_type: index === 0 ? 'create' : 'renew',
        operation_time: serial.created_at,
        start_date: serial.start_date,
        end_date: serial.expires_at,
        duration: serial.valid_days,
        amount: serial.amount,
        payment_status: serial.payment_status
      }))
    }
  } catch (error) {
    console.error('获取租赁历史失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听对话框显示状态
watch(() => props.show, async (newVal) => {
  if (newVal && props.rental) {
    await fetchRentalHistory()
  }
})
</script>

<template>
  <BaseDialogR :show="show" @close="$emit('close')" class="max-w-full mx-8">
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-lg font-bold">租赁详情</span>
        <BaseButton color="info" label="关闭" small @click="$emit('close')" />
      </div>
    </template>

    <template #default>
      <div class="space-y-6">
        <!-- 搜索框 -->
        <div class="flex justify-end">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索序列号..."
            class="px-3 py-2 border rounded-md w-64"
          />
        </div>

        <!-- 历史记录表格 -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作时间</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作类型</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">序列号</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">时长</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">开始时间</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">结束时间</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">金额</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">支付状态</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-if="loading">
                  <td colspan="8" class="px-4 py-4 text-center text-gray-500">加载中...</td>
                </tr>
                <tr v-else-if="filteredHistory.length === 0">
                  <td colspan="8" class="px-4 py-4 text-center text-gray-500">
                    {{ searchQuery ? '没有找到匹配的记录' : '暂无历史记录' }}
                  </td>
                </tr>
                <tr v-for="(record, index) in filteredHistory" :key="index" 
                    :class="{'bg-green-50': record.operation_type === 'create'}">
                  <td class="px-4 py-3">{{ formatDate(record.operation_time) }}</td>
                  <td class="px-4 py-3">
                    <span :class="{
                      'px-2 py-1 rounded-full text-xs font-medium': true,
                      'bg-green-100 text-green-800': record.operation_type === 'create',
                      'bg-blue-100 text-blue-800': record.operation_type === 'renew'
                    }">
                      {{ record.operation_type === 'create' ? '创建' : '续费' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 font-mono">{{ record.serial_code }}</td>
                  <td class="px-4 py-3">{{ record.duration }}天</td>
                  <td class="px-4 py-3">{{ formatDate(record.start_date) }}</td>
                  <td class="px-4 py-3">{{ formatDate(record.end_date) }}</td>
                  <td class="px-4 py-3">¥{{ record.amount }}</td>
                  <td class="px-4 py-3">
                    <span :class="{
                      'px-2 py-1 rounded-full text-xs font-medium': true,
                      'bg-green-100 text-green-800': record.payment_status === 'paid',
                      'bg-red-100 text-red-800': record.payment_status === 'unpaid',
                      'bg-yellow-100 text-yellow-800': record.payment_status === 'pending'
                    }">
                      {{ record.payment_status === 'paid' ? '已支付' : 
                         record.payment_status === 'unpaid' ? '未支付' : '处理中' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </BaseDialogR>
</template>

<style scoped>
.hover\:bg-gray-50:hover {
  @apply bg-gray-50 transition-colors duration-150;
}

/* 确保表格内容有合适的间距 */
td, th {
  @apply px-6 py-4 whitespace-nowrap;
}
</style> 
