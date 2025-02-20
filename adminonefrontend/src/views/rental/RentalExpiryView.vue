<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { 
  mdiCalendarClock,
  mdiBellRing,
  mdiRefresh,
  mdiEmailOutline
} from '@mdi/js'
import api from '@/services/api'

// 租赁列表数据
const rentals = ref([])
const loading = ref(false)
const sendingEmail = ref(false)

// 过滤5天内到期的租赁
const expiringWithin5Days = computed(() => {
  return rentals.value.filter(rental => {
    const daysRemaining = Math.ceil((new Date(rental.end_date) - new Date()) / (1000 * 60 * 60 * 24))
    return daysRemaining <= 5 && daysRemaining > 0
  })
})

// 过滤5-10天内到期的租赁
const expiringWithin10Days = computed(() => {
  return rentals.value.filter(rental => {
    const daysRemaining = Math.ceil((new Date(rental.end_date) - new Date()) / (1000 * 60 * 60 * 24))
    return daysRemaining > 5 && daysRemaining <= 10
  })
})

// 获取所有租赁
const fetchRentals = async () => {
  try {
    loading.value = true
    const response = await api.getRentals()
    if (response.success) {
      rentals.value = response.rentals.map(rental => ({
        ...rental,
        user_email: rental.user_info?.email || rental.email || '邮箱未设置'
      }))
    }
  } catch (error) {
    console.error('获取租赁列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 发送续费提醒邮件
const sendRenewalEmail = async (rental) => {
  try {
    sendingEmail.value = true
    if (!rental.user_email || rental.user_email === '邮箱未设置') {
      throw new Error('用户邮箱未设置')
    }
    const response = await api.sendReminderNotification({
      user_id: rental.user_id,
      email: rental.user_email,
      type: 'renewal',
      data: {
        expiry_date: rental.end_date,
        days_remaining: getRemainingDays(rental.end_date)
      }
    })
    
    if (response.success) {
      alert(`已成功发送续费提醒邮件给用户 ${rental.user_email}`)
    }
  } catch (error) {
    console.error('发送续费提醒邮件失败:', error)
    alert('发送邮件失败: ' + (error.message || '未知错误'))
  } finally {
    sendingEmail.value = false
  }
}

// 计算剩余天数
const getRemainingDays = (endDate) => {
  const days = Math.ceil((new Date(endDate) - new Date()) / (1000 * 60 * 60 * 24))
  return days > 0 ? days : 0
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

onMounted(fetchRentals)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <!-- 5天内到期的租赁 -->
      <CardBox class="mb-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-xl font-bold text-red-600">
            <BaseIcon :path="mdiCalendarClock" class="inline-block mr-2" />
            5天内到期
          </h1>
          <BaseButton
            :icon="mdiRefresh"
            color="info"
            :loading="loading"
            @click="fetchRentals"
          />
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">用户邮箱</th>
                <th class="px-4 py-3 text-left">到期时间</th>
                <th class="px-4 py-3 text-left">剩余天数</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">流量使用</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rental in expiringWithin5Days" :key="rental.id">
                <td class="px-4 py-3">
                  <span :class="{'text-red-500': !rental.user_email || rental.user_email === '邮箱未设置'}">
                    {{ rental.user_email }}
                  </span>
                </td>
                <td class="px-4 py-3">{{ new Date(rental.end_date).toLocaleString() }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                    {{ getRemainingDays(rental.end_date) }}天
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded-full text-xs': true,
                    'bg-green-100 text-green-800': rental.status === 'active',
                    'bg-red-100 text-red-800': rental.status === 'expired',
                    'bg-yellow-100 text-yellow-800': rental.status === 'pending'
                  }">
                    {{ formatStatus(rental.status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  {{ rental.total_traffic }}GB
                </td>
                <td class="px-4 py-3">
                  <BaseButton
                    :icon="mdiEmailOutline"
                    color="info"
                    small
                    :loading="sendingEmail"
                    :disabled="!rental.user_email || rental.user_email === '邮箱未设置'"
                    @click="sendRenewalEmail(rental)"
                    :title="rental.user_email === '邮箱未设置' ? '用户邮箱未设置' : '发送续费提醒'"
                  />
                </td>
              </tr>
              <tr v-if="expiringWithin5Days.length === 0">
                <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                  暂无5天内到期的租赁
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>

      <!-- 5-10天内到期的租赁 -->
      <CardBox>
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-xl font-bold text-yellow-600">
            <BaseIcon :path="mdiCalendarClock" class="inline-block mr-2" />
            5-10天内到期
          </h1>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">用户邮箱</th>
                <th class="px-4 py-3 text-left">到期时间</th>
                <th class="px-4 py-3 text-left">剩余天数</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">流量使用</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rental in expiringWithin10Days" :key="rental.id">
                <td class="px-4 py-3">{{ rental.user_email }}</td>
                <td class="px-4 py-3">{{ new Date(rental.end_date).toLocaleString() }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                    {{ getRemainingDays(rental.end_date) }}天
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded-full text-xs': true,
                    'bg-green-100 text-green-800': rental.status === 'active',
                    'bg-red-100 text-red-800': rental.status === 'expired',
                    'bg-yellow-100 text-yellow-800': rental.status === 'pending'
                  }">
                    {{ formatStatus(rental.status) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  {{ rental.total_traffic }}GB
                </td>
                <td class="px-4 py-3">
                  <BaseButton
                    :icon="mdiEmailOutline"
                    color="info"
                    small
                    :loading="sendingEmail"
                    @click="sendRenewalEmail(rental)"
                    title="发送续费提醒"
                  />
                </td>
              </tr>
              <tr v-if="expiringWithin10Days.length === 0">
                <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                  暂无5-10天内到期的租赁
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
