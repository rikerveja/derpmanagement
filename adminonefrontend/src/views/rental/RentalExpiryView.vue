<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { 
  mdiCalendarClock,
  mdiBellRing,
  mdiRefresh,
  mdiDelete
} from '@mdi/js'
import api from '@/services/api'

// 即将到期的租赁列表
const expiringRentals = ref([])
const daysToExpiry = ref(7)
const loading = ref(false)

// 获取即将到期的租赁
const fetchExpiringRentals = async () => {
  try {
    loading.value = true
    const response = await api.getExpiringRentals(daysToExpiry.value)
    if (response.success) {
      expiringRentals.value = response.rentals
    }
  } catch (error) {
    console.error('获取即将到期租赁失败:', error)
    alert('获取数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 发送到期通知
const sendNotifications = async () => {
  try {
    loading.value = true
    const response = await api.sendExpiryNotifications({ days_to_expiry: daysToExpiry.value })
    if (response.success) {
      alert('通知发送成功!')
      await fetchExpiringRentals()
    }
  } catch (error) {
    console.error('发送通知失败:', error)
    alert('发送通知失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 检查并处理到期租赁
const checkExpiry = async () => {
  try {
    loading.value = true
    const response = await api.checkRentalExpiry()
    if (response.success) {
      alert('已成功处理到期租赁!')
      await fetchExpiringRentals()
    }
  } catch (error) {
    console.error('处理到期租赁失败:', error)
    alert('处理失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 释放资源
const releaseResources = async (rentalId) => {
  if (!confirm('确定要释放该租赁的所有资源吗？此操作不可恢复!')) {
    return
  }
  
  try {
    loading.value = true
    const response = await api.deleteRental(rentalId)
    if (response.success) {
      alert('资源释放成功!')
      await fetchExpiringRentals()
    }
  } catch (error) {
    console.error('释放资源失败:', error)
    alert('释放失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 添加计算属性来格式化状态显示
const formatStatus = (status) => {
  const statusMap = {
    'active': '使用中',
    'expired': '已到期',
    'pending': '待激活'
  }
  return statusMap[status] || status
}

onMounted(fetchExpiringRentals)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox class="mb-6">
        <!-- 标题栏 -->
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold">到期检查</h1>
          <div class="flex space-x-2">
            <div class="flex items-center">
              <span class="mr-2">提前天数:</span>
              <input
                v-model.number="daysToExpiry"
                type="number"
                min="1"
                class="w-20 px-2 py-1 border rounded"
              />
            </div>
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              :loading="loading"
              @click="fetchExpiringRentals"
              title="刷新"
            />
            <BaseButton
              :icon="mdiBellRing"
              color="warning"
              :loading="loading"
              @click="sendNotifications"
              title="发送通知"
            />
            <BaseButton
              :icon="mdiCalendarClock"
              color="danger"
              :loading="loading"
              @click="checkExpiry"
              title="处理到期"
            />
          </div>
        </div>

        <!-- 即将到期的租赁列表 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">用户ID</th>
                <th class="px-4 py-3 text-left">序列号</th>
                <th class="px-4 py-3 text-left">到期时间</th>
                <th class="px-4 py-3 text-left">剩余天数</th>
                <th class="px-4 py-3 text-left">续费次数</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="rental in expiringRentals" :key="rental.id">
                <td class="px-4 py-3">{{ rental.user_id }}</td>
                <td class="px-4 py-3">{{ rental.serial_code }}</td>
                <td class="px-4 py-3">{{ new Date(rental.end_date).toLocaleString() }}</td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded-full text-xs': true,
                    'bg-red-100 text-red-800': rental.days_remaining <= 3,
                    'bg-yellow-100 text-yellow-800': rental.days_remaining > 3 && rental.days_remaining <= daysToExpiry,
                    'bg-green-100 text-green-800': rental.days_remaining > daysToExpiry
                  }">
                    {{ rental.days_remaining }}天
                  </span>
                </td>
                <td class="px-4 py-3">{{ rental.renewal_count }}</td>
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
                  <BaseButton
                    :icon="mdiDelete"
                    color="danger"
                    small
                    :loading="loading"
                    @click="releaseResources(rental.id)"
                    title="释放资源"
                  />
                </td>
              </tr>
              <tr v-if="expiringRentals.length === 0">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  暂无即将到期的租赁
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
input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}
</style> 