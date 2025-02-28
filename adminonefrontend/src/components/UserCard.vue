<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/auth'
import BaseLevel from '@/components/BaseLevel.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiCheck, mdiAccount } from '@mdi/js'

const mainStore = useMainStore()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '未登录'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取登录位置（如果后端没有提供，可以先写"本地登录"）
const getLoginLocation = () => {
  return '本地登录'
}
</script>

<template>
  <CardBox>
    <BaseLevel>
      <div class="flex items-center justify-start">
        <UserAvatar 
          class="w-12 h-12 md:w-16 md:h-16" 
          :username="user?.username"
        />
        <div class="ml-4">
          <h4 class="text-xl font-semibold">{{ user?.username }}</h4>
          <p class="text-gray-500">{{ user?.email }}</p>
          <div class="text-sm text-gray-500 mt-1">
            <div>最近登录时间: {{ formatDateTime(user?.last_login) }}</div>
            <div>来自: {{ getLoginLocation() }}</div>
          </div>
        </div>
      </div>
      <div class="flex">
        <BaseButtons>
          <BaseButton
            :icon="mdiCheck"
            :label="user?.is_verified ? '已验证' : '未验证'"
            :color="user?.is_verified ? 'success' : 'warning'"
            small
          />
        </BaseButtons>
      </div>
    </BaseLevel>
  </CardBox>
</template>
