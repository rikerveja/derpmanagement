<script setup>
import { computed, ref } from 'vue'
import { useMainStore } from '@/stores/main'
import { mdiCheckDecagram } from '@mdi/js'
import BaseLevel from '@/components/BaseLevel.vue'
import UserAvatarCurrentUser from '@/components/UserAvatarCurrentUser.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import PillTag from '@/components/PillTag.vue'

const mainStore = useMainStore()

const userName = computed(() => mainStore.userName)

const lastLogin = computed(() => {
  const lastLoginTime = localStorage.getItem('last_login')
  if (!lastLoginTime) return '未登录'
  
  // 计算距离上次登录的时间
  const lastLoginDate = new Date(lastLoginTime)
  const now = new Date()
  const diff = Math.floor((now - lastLoginDate) / 1000 / 60) // 转换为分钟
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return lastLoginDate.toLocaleString()
})

const lastLoginIp = computed(() => localStorage.getItem('last_login_ip') || '未知')

const userSwitchVal = ref(false)
</script>

<template>
  <CardBox>
    <BaseLevel type="justify-around lg:justify-center">
      <UserAvatarCurrentUser class="lg:mx-12" />
      <div class="space-y-3 text-center md:text-left lg:mx-12">
        <div class="flex justify-center md:block">
          <FormCheckRadio
            v-model="userSwitchVal"
            name="notifications-switch"
            type="switch"
            label="通知"
            :input-value="true"
          />
        </div>
        <h1 class="text-2xl">
          你好, <b>{{ userName }}</b>!
        </h1>
        <p>最近登录时间 <b>{{ lastLogin }}</b> 来自 <b>{{ lastLoginIp }}</b></p>
        <div class="flex justify-center md:block">
          <PillTag label="已验证" color="info" :icon="mdiCheckDecagram" />
        </div>
      </div>
    </BaseLevel>
  </CardBox>
</template>
