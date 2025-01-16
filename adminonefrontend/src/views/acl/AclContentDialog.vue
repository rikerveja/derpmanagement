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
          :label="copySuccess ? '已复制' : '复制'"
          small
          @click="copyToClipboard"
          :class="{ 'copy-success': copySuccess }"
          :disabled="copySuccess"
        />
      </div>
    </template>
    
    <template #body>
      <div class="max-h-[60vh] overflow-y-auto">
        <pre ref="contentRef" class="bg-gray-50 p-4 rounded-lg text-sm font-mono whitespace-pre-wrap">{{ content }}</pre>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-end">
        <BaseButton
          label="关闭"
          color="info"
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
  content: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])
const copySuccess = ref(false)
const contentRef = ref(null)

const copyToClipboard = async () => {
  if (!props.content) return
  
  try {
    // 使用现代 Clipboard API
    await navigator.clipboard.writeText(props.content)
    
    // 复制成功处理
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (err) {
    // 如果 Clipboard API 失败，尝试备用方案
    try {
      // 创建临时文本区域
      const textArea = document.createElement('textarea')
      textArea.value = props.content
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      
      // 复制成功处理
      copySuccess.value = true
      setTimeout(() => {
        copySuccess.value = false
      }, 2000)
    } catch (error) {
      console.error('复制失败:', error)
      alert('复制失败，请手动复制')
    }
  }
}
</script>

<style scoped>
pre {
  max-width: 100%;
  overflow-x: auto;
  tab-size: 4;
}

.copy-success {
  @apply bg-green-500 text-white cursor-not-allowed opacity-75;
}

/* 添加过渡效果 */
.copy-button {
  transition: all 0.2s ease-in-out;
}

/* 美化滚动条 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.400') theme('colors.gray.100');
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded hover:bg-gray-500;
}
</style> 
