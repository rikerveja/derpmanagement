<script setup>
import { reactive, ref, onMounted, onBeforeUnmount } from 'vue'
import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/auth'
import { mdiAccount, mdiMail, mdiAsterisk, mdiFormTextboxPassword } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import FormFilePicker from '@/components/FormFilePicker.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import UserCard from '@/components/UserCard.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import RentalRenewDialog from '@/views/rental/RentalRenewDialog.vue'
import api from '@/services/api'

const mainStore = useMainStore()
const authStore = useAuthStore()
const user = ref(authStore.user)
const rentalInfo = ref(null)
const showDialog = ref(false)
const isComponentActive = ref(true)
const userCard = ref(null)

const profileForm = reactive({
  username: user.value?.username || '',
  email: user.value?.email || '',
  current_password: '',
  avatar: null
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const submitProfile = async () => {
  try {
    const updateData = {
      user_id: user.value.id,
      username: profileForm.username,
      password: profileForm.current_password
    }

    const response = await api.updateProfile(updateData)
    
    if (response.success) {
      alert('个人资料更新成功')
      authStore.updateUser({
        ...user.value,
        username: profileForm.username
      })
      if (userCard.value) {
        userCard.value.avatarUrl = user.value?.avatar || ''
      }
      profileForm.current_password = ''
    }
  } catch (error) {
    alert(error.message || '更新失败')
  }
}

const submitPassword = async () => {
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    alert('两次输入的新密码不一致')
    return
  }
  
  try {
    const updateData = {
      user_id: user.value.id,
      password: passwordForm.current_password,
      new_password: passwordForm.new_password
    }
    
    const response = await api.updateProfile(updateData)
    
    if (response.success) {
      alert('密码修改成功')
      passwordForm.current_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    }
  } catch (error) {
    alert(error.message || '修改失败')
  }
}

const fetchRentalInfo = async () => {
  try {
    if (!isComponentActive.value) return
    const userId = JSON.parse(localStorage.getItem('user'))?.id
    const response = await api.getRentalHistory(userId)
    console.log('获取到的历史数据:', response)
    
    if (!isComponentActive.value) return
    if (response.success && response.history?.length > 0) {
      const historyRecords = response.history.map(record => ({
        ...record,
        total_traffic: typeof record.total_traffic === 'number' 
          ? record.total_traffic 
          : parseFloat(record.total_traffic || '0'),
        traffic_limit: typeof record.traffic_limit === 'number'
          ? record.traffic_limit
          : parseFloat(record.traffic_limit || '5'),
        start_date: record.start_date,
        end_date: record.end_date,
        renewal_count: parseInt(record.renewal_count || 0)
      }))
      
      const latestRental = historyRecords[0]
      
      rentalInfo.value = {
        expiry_date: formatDate(latestRental.end_date),
        remaining_days: calculateRemainingDays(latestRental.end_date),
        total_traffic: latestRental.total_traffic || 0, // 已经是 GB 单位
        traffic_limit: latestRental.traffic_limit || 5, // 已经是 GB 单位
        server_list: latestRental.server_ips || [], // 使用服务器 IP 列表
        container_status: latestRental.status || 'pending',
        server_status: latestRental.status || 'pending',
        payment_status: latestRental.payment_status || 'pending'
      }
      console.log('处理后的租约信息:', rentalInfo.value)
    } else {
      rentalInfo.value = {
        expiry_date: '暂无数据',
        remaining_days: 0,
        total_traffic: 0,
        traffic_limit: 5, // 默认 5GB
        server_list: [],
        container_status: 'pending',
        server_status: 'pending',
        payment_status: 'pending'
      }
      console.log('无租约信息')
    }
  } catch (error) {
    if (isComponentActive.value) {
      console.error('获取租约信息失败:', error)
      alert('获取租约信息失败')
    }
  }
}

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

const calculateRemainingDays = (expiryDate) => {
  if (!expiryDate) return 0
  const now = new Date()
  const expiry = new Date(expiryDate)
  const diffTime = expiry - now
  const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return days > 0 ? days : 0
}

const formatTraffic = (gb) => {
  if (!gb) return '0 GB'
  return `${gb.toFixed(2)} GB`
}

const formatContainerStatus = (status) => {
  const statusMap = {
    'running': '运行中',
    'stopped': '已停止',
    'pending': '处理中',
    'error': '错误'
  }
  return statusMap[status] || status
}

const formatServerStatus = (status) => {
  const statusMap = {
    'running': '运行中',
    'stopped': '已停止',
    'pending': '处理中',
    'error': '错误'
  }
  return statusMap[status] || status
}

const formatStatus = (status) => {
  const statusMap = {
    'active': '使用中',
    'expired': '已到期',
    'pending': '待激活'
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

const showRenewDialog = () => {
  showDialog.value = true
}

const handleRenewSuccess = () => {
  showDialog.value = false
  fetchRentalInfo()
  alert('续约成功')
}

onMounted(() => {
  isComponentActive.value = true
  fetchRentalInfo()
})

onBeforeUnmount(() => {
  isComponentActive.value = false
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccount" title="个人资料" main />

      <UserCard ref="userCard" class="mb-6" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CardBox is-form @submit.prevent="submitProfile">
          <FormField label="头像" help="最大 500kb">
            <FormFilePicker label="上传" />
          </FormField>

          <FormField label="姓名" help="必填项。您的姓名">
            <FormControl
              v-model="profileForm.username"
              :icon="mdiAccount"
              name="username"
              required
              autocomplete="username"
            />
          </FormField>
          <FormField label="邮箱" help="必填项。您的邮箱">
            <FormControl
              v-model="profileForm.email"
              :icon="mdiMail"
              type="email"
              name="email"
              required
              autocomplete="email"
            />
          </FormField>

          <template #footer>
            <BaseButtons>
              <BaseButton color="info" type="submit" label="提交" />
              <BaseButton color="info" label="选项" outline />
            </BaseButtons>
          </template>
        </CardBox>

        <CardBox is-form @submit.prevent="submitPassword">
          <FormField label="当前密码" help="必填项。您的当前密码">
            <FormControl
              v-model="passwordForm.current_password"
              :icon="mdiAsterisk"
              name="current_password"
              type="password"
              required
              autocomplete="current-password"
            />
          </FormField>

          <BaseDivider />

          <FormField label="新密码" help="必填项。新密码">
            <FormControl
              v-model="passwordForm.new_password"
              :icon="mdiFormTextboxPassword"
              name="new_password"
              type="password"
              required
              autocomplete="new-password"
            />
          </FormField>

          <FormField label="确认密码" help="必填项。再次输入新密码">
            <FormControl
              v-model="passwordForm.confirm_password"
              :icon="mdiFormTextboxPassword"
              name="confirm_password"
              type="password"
              required
              autocomplete="new-password"
            />
          </FormField>

          <template #footer>
            <BaseButtons>
              <BaseButton type="submit" color="info" label="提交" />
              <BaseButton color="info" label="选项" outline />
            </BaseButtons>
          </template>
        </CardBox>
      </div>

      <CardBox class="mt-6">
        <div class="rental-info">
          <h3 class="text-lg font-bold mb-4">租约信息</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-gray-600">到期时间：</span>
              <span>{{ rentalInfo?.expiry_date || '暂无数据' }}</span>
            </div>
            <div>
              <span class="text-gray-600">剩余天数：</span>
              <span>{{ rentalInfo?.remaining_days }} 天</span>
            </div>
            <div>
              <span class="text-gray-600">流量使用：</span>
              <span>{{ formatTraffic(rentalInfo?.total_traffic) }}/{{ formatTraffic(rentalInfo?.traffic_limit) }}</span>
            </div>
            <div>
              <span class="text-gray-600">服务器：</span>
              <span>{{ rentalInfo?.server_list?.length ? rentalInfo.server_list.join(', ') : '暂无' }}</span>
            </div>
            <div>
              <span class="text-gray-600">容器状态：</span>
              <span :class="{
                'text-green-600': rentalInfo?.container_status === 'running',
                'text-red-600': rentalInfo?.container_status === 'stopped',
                'text-yellow-600': rentalInfo?.container_status === 'pending'
              }">
                {{ formatContainerStatus(rentalInfo?.container_status) }}
              </span>
            </div>
            <div>
              <span class="text-gray-600">服务器状态：</span>
              <span :class="{
                'text-green-600': rentalInfo?.server_status === 'running',
                'text-red-600': rentalInfo?.server_status === 'stopped',
                'text-yellow-600': rentalInfo?.server_status === 'pending'
              }">
                {{ formatServerStatus(rentalInfo?.server_status) }}
              </span>
            </div>
          </div>
          
          <div class="mt-4">
            <BaseButton
              color="info"
              @click="showRenewDialog"
              :disabled="!rentalInfo"
              label="续约服务"
            />
          </div>
        </div>
      </CardBox>

      <RentalRenewDialog
        v-if="showDialog"
        :show="showDialog"
        :rental="rentalInfo"
        @close="showDialog = false"
        @success="handleRenewSuccess"
      />
    </SectionMain>
  </LayoutAuthenticated>
</template>
