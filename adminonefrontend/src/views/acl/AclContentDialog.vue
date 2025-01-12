<template>
  <BaseDialog
    :show="show"
    @close="$emit('close')"
    :has-cancel="false"
  >
    <template #title>
      <div class="flex justify-between items-center">
        <span>ACL 配置内容</span>
        <BaseButton
          :icon="mdiContentCopy"
          :color="copySuccess ? 'success' : 'info'"
          small
          @click="copyToClipboard"
          :label="copySuccess ? '已复制' : '复制'"
          class="ml-4"
        />
      </div>
    </template>
    
    <template #body>
      <div class="max-h-[60vh] overflow-y-auto">
        <pre class="bg-gray-50 p-4 rounded-lg text-sm font-mono whitespace-pre-wrap">{{ content }}</pre>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-end">
        <BaseButton
          label="关闭"
          @click="$emit('close')"
        />
      </div>
    </template>
  </BaseDialog>
</template>

<script setup>
import { ref } from 'vue'
import BaseDialog from '@/components/BaseDialog.vue'
import BaseButton from '@/components/BaseButton.vue'
import { mdiContentCopy } from '@mdi/js'

const props = defineProps({
  show: Boolean,
  content: String
})

const emit = defineEmits(['close'])
const copySuccess = ref(false)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.content)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
    alert('复制失败: ' + error.message)
  }
}
</script>

<style scoped>
pre {
  max-width: 100%;
  overflow-x: auto;
}

.copy-button {
  transition: all 0.2s;
}

.copy-success {
  @apply bg-green-500 text-white;
}
</style> 