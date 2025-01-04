<script setup>
import { useAuthStore } from '@/stores/auth'
import NavBarItem from '@/components/NavBarItem.vue'

defineProps({
  menu: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['menu-click'])

const menuClick = (event, item) => {
  emit('menu-click', event, item)
}
</script>

<template>
  <ul>
    <li v-for="(item, index) in menu" :key="index">
      <NavBarItem :item="item" @menu-click="menuClick" />
    </li>
  </ul>
</template>
