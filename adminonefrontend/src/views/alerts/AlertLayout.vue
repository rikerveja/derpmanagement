<script setup>
import { ref } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import NavBar from '@/components/NavBar.vue'
import { mdiBell, mdiCog } from '@mdi/js'

const menuNavBar = [
  {
    icon: mdiBell,
    label: '告警列表',
    to: '/alerts'
  },
  {
    icon: mdiCog,
    label: '告警设置',
    to: '/alerts/settings'
  }
]
</script>

<template>
  <LayoutAuthenticated>
    <NavBar
      :menu="menuNavBar"
      class="mb-6"
    />
    <router-view />
  </LayoutAuthenticated>
</template> 