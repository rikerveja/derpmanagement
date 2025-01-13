<template>
  <div v-if="show" class="fixed inset-0 z-50">
    <!-- 背景遮罩 -->
    <div class="fixed inset-0 bg-black bg-opacity-50" @click="handleClose"></div>
    
    <!-- 对话框 -->
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        <!-- 标题栏 -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="text-lg font-semibold text-gray-900 dark:text-white">
            <slot name="header">对话框标题</slot>
          </div>
        </div>
        
        <!-- 内容区域 -->
        <div class="px-6 py-4 overflow-y-auto">
          <slot name="default">对话框内容</slot>
        </div>
        
        <!-- 底部按钮区域 -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <slot name="footer">
            <div class="flex justify-end space-x-2">
              <slot name="actions"></slot>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const handleClose = () => {
  emit('close')
}
</script>

<script>
export default {
  name: 'BaseDialog'
}
</script>

<style scoped>
/* 添加淡入淡出动画 */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style> 