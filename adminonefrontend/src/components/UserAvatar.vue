<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    default: null
  },
  api: {
    type: String,
    default: 'avataaars'
  }
})

// 生成统一的头像 URL
const avatarUrl = computed(() => {
  // 如果用户名存在，则生成头像
  if (props.username) {
    return `https://api.dicebear.com/7.x/${props.api}/svg?seed=${props.username.replace(
      /[^a-z0-9]+/gi,
      '-'
    )}.svg`
  }
  // 如果没有用户名，返回默认头像
  return `https://api.dicebear.com/7.x/${props.api}/svg?seed=default`
})
</script>

<template>
  <div class="relative inline-block">
    <img 
      :src="avatarUrl" 
      :alt="username"
      class="rounded-full w-full h-full object-cover bg-gray-100 dark:bg-gray-800"
    />
  </div>
</template>

<style scoped>
.relative {
  aspect-ratio: 1;
}
</style>
