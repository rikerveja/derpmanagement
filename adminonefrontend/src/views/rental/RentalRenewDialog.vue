<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import BaseDialogR from '@/components/BaseDialogR.vue'
import BaseButton from '@/components/BaseButton.vue'
import SearchSelect from '@/components/SearchSelect.vue'
import api from '@/services/api'
import { formatDate } from '@/utils/format'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  rental: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'renew'])

// 添加一个变量存储当前序列号
const currentSerialCode = ref('')

// 表单数据
const renewalForm = ref({
  serial_code: '',        // 续费序列号（新序列号）
  renewal_amount: 0,      // 续费金额
  renewal_period: 0       // 续费时长
})

// 可用序列号列表
const serialList = ref([])
const selectedSerial = ref(null)

// 加载状态
const loading = ref({
  serials: false,
  submit: false
})
const error = ref('')

// 计算新的到期时间
const newExpiryDate = computed(() => {
  if (!selectedSerial.value || !props.rental.end_date) return null
  
  // 从序列号中获取天数（假设前3位是天数）
  const days = parseInt(selectedSerial.value.serial_code.slice(0, 3))
  if (isNaN(days)) return null
  
  // 从当前到期时间开始计算
  const currentExpiry = new Date(props.rental.end_date)
  const newExpiry = new Date(currentExpiry.getTime())
  newExpiry.setDate(newExpiry.getDate() + days)
  
  return newExpiry
})

// 获取序列号列表
const fetchSerials = async () => {
  try {
    loading.value.serials = true
    const response = await api.getSerials()
    console.log('序列号列表响应:', response)
    if (response && response.serial_numbers) {
      serialList.value = response.serial_numbers
        .filter(serial => serial.status === 'unused')
        .map(serial => ({
          ...serial,
          label: `${serial.serial_code} ${serial.type ? `- ${serial.type}` : ''}`
        }))
    }
  } catch (error) {
    console.error('获取序列号列表失败:', error)
    error.value = '获取序列号列表失败'
  } finally {
    loading.value.serials = false
  }
}

// 处理序列号选择
const handleSerialSelect = (serial) => {
  selectedSerial.value = serial
  renewalForm.value.serial_code = serial.serial_code
  // 从序列号中提取天数
  renewalForm.value.renewal_period = parseInt(serial.serial_code.slice(0, 3)) || 0
}

// 处理续费
const handleRenew = async () => {
  if (loading.value.submit) return
  if (!renewalForm.value.serial_code || !renewalForm.value.renewal_amount) {
    error.value = '请选择续费序列号并填写续费金额'
    return
  }

  try {
    loading.value.submit = true
    const response = await api.renewRental({
      serial_code: renewalForm.value.serial_code,      // 新的续约序列号
      user_id: props.rental.user_id,                   // 从 rental 对象中获取用户 ID
      renewal_amount: renewalForm.value.renewal_amount, // 续费金额
      renewal_period: renewalForm.value.renewal_period  // 续费时长
    })

    // 续费成功，直接关闭对话框并刷新列表
    emit('renew', { refresh: true })
    handleClose()
  } catch (err) {
    console.error('续费请求失败:', err)
    error.value = '网络请求失败，请检查网络连接'
  } finally {
    loading.value.submit = false
  }
}

// 关闭处理函数
const handleClose = () => {
  renewalForm.value = {
    serial_code: '',
    renewal_amount: 0,
    renewal_period: 0
  }
  selectedSerial.value = null
  error.value = ''
  emit('close')
}

// 监听 rental 变化，更新当前序列号
watch(() => props.rental, (newRental) => {
  if (newRental) {
    currentSerialCode.value = newRental.serial_code  // 存储当前序列号
  }
}, { immediate: true })

// 监听对话框显示状态
watch(() => props.show, async (newVal) => {
  if (newVal) {
    // 对话框打开时获取可用序列号
    await fetchSerials()
  } else {
    handleClose()
  }
})

onMounted(() => {
  fetchSerials() // 组件加载时获取序列号列表
})
</script>

<template>
  <BaseDialogR :show="show" @close="handleClose">
    <template #header>
      <div class="text-lg font-bold">续费租赁</div>
    </template>

    <template #default>
      <div class="grid gap-4">
        <!-- 错误提示 -->
        <div v-if="error" class="text-red-500 text-sm">
          {{ error }}
        </div>

        <!-- 用户信息 -->
        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-2">续费用户信息</h3>
          <div class="space-y-1">
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-20">用户名：</span>
              <span class="font-medium">{{ rental.username }}</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-20">邮箱：</span>
              <span class="font-medium">{{ rental.email }}</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-20">当前到期：</span>
              <span class="font-medium">{{ formatDate(rental.end_date) }}</span>
            </div>
          </div>
        </div>

        <!-- 当前序列号显示 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">当前序列号</label>
          <input
            v-model="currentSerialCode"
            type="text"
            class="w-full px-3 py-2 border rounded-md bg-gray-50"
            disabled
          />
        </div>

        <!-- 新序列号选择 -->
        <div class="form-group">
          <SearchSelect
            label="续费序列号"
            :items="serialList"
            :loading="loading.serials"
            @select="handleSerialSelect"
          >
            <template #item="{ item }">
              <div class="flex justify-between items-center">
                <span>{{ item.serial_code }}</span>
                <span class="text-sm text-gray-500">{{ item.days }}天</span>
              </div>
            </template>
          </SearchSelect>
          
          <!-- 新的到期时间显示 -->
          <div v-if="selectedSerial && newExpiryDate" 
               class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div class="flex items-center text-sm">
              <span class="text-blue-600 font-medium">续费后的新到期时间：</span>
            </div>
            <div class="mt-1 text-lg font-bold text-blue-700">
              {{ formatDate(newExpiryDate) }}
            </div>
            <div class="mt-1 text-xs text-blue-500">
              将延长 {{ selectedSerial.serial_code.slice(0,3) }} 天
            </div>
          </div>
        </div>

        <!-- 续费金额 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">续费金额</label>
          <input
            v-model.number="renewalForm.renewal_amount"
            type="number"
            min="0"
            step="0.01"
            class="w-full px-3 py-2 border rounded-md"
            placeholder="请输入续费金额"
            :disabled="loading.submit"
          />
        </div>

        <!-- 提示信息 -->
        <div class="text-sm text-gray-500">
          注意：
          <ul class="list-disc list-inside mt-1">
            <li>续费后将自动延长租赁期限</li>
            <li>新的租赁期限将从当前租赁到期时间开始计算</li>
            <li>系统会同步更新容器和 ACL 的到期时间</li>
          </ul>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          color="info"
          label="取消"
          @click="handleClose"
          :disabled="loading.submit"
        />
        <BaseButton
          color="success"
          :label="loading.submit ? '处理中...' : '确认续费'"
          @click="handleRenew"
          :disabled="loading.submit || !selectedSerial || !renewalForm.renewal_amount"
          :loading="loading.submit"
        />
      </div>
    </template>
  </BaseDialogR>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}

/* 添加动画效果 */
.bg-blue-50 {
  transition: all 0.3s ease-in-out;
}

.bg-blue-50:hover {
  transform: scale(1.01);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style> 
