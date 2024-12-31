<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'
import BaseLevel from '@/components/BaseLevel.vue'
import UserAvatar from '@/components/UserAvatar.vue'

const mainStore = useMainStore()

const userName = computed(() => mainStore.userName)
const userEmail = computed(() => localStorage.getItem('userEmail') || '未登录')
</script>

<template>
  <BaseLevel>
    <div class="flex items-center justify-start">
      <UserAvatar class="w-12 h-12 mr-3" />
      <div class="flex flex-col">
        <span class="text-lg font-semibold">{{ userEmail }}</span>
        <span class="text-sm text-gray-500">管理员</span>
      </div>
    </div>
  </BaseLevel>
</template>
