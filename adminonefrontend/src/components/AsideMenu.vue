<script setup>
import { useRouter } from 'vue-router'
import AsideMenuLayer from '@/components/AsideMenuLayer.vue'
import OverlayLayer from '@/components/OverlayLayer.vue'

defineProps({
  menu: {
    type: Array,
    required: true
  },
  isAsideMobileExpanded: Boolean,
  isAsideLgActive: Boolean
})

const emit = defineEmits(['menu-click', 'aside-lg-close-click'])
const router = useRouter()

const menuClick = (event, item) => {
  if (item.isLogout) {
    logout()
  } else {
    emit('menu-click', event, item)
  }
}

const asideLgCloseClick = (event) => {
  emit('aside-lg-close-click', event)
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<template>
  <AsideMenuLayer
    :menu="menu"
    :class="[
      isAsideMobileExpanded ? 'left-0' : '-left-60 lg:left-0',
      { 'lg:hidden xl:flex': !isAsideLgActive }
    ]"
    @menu-click="menuClick"
    @aside-lg-close-click="asideLgCloseClick"
  />
  <OverlayLayer v-show="isAsideLgActive" z-index="z-30" @overlay-click="asideLgCloseClick" />
</template>
