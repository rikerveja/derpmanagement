<template>
  <div v-if="show" class="fixed inset-0 z-50">
    <!-- 背景遮罩 -->
    <div class="fixed inset-0 bg-black bg-opacity-50" @click="handleClose"></div>
    
    <!-- 对话框 -->
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl flex flex-col max-h-[90vh]">
        <!-- 标题栏 -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <div class="text-lg font-semibold text-gray-900 dark:text-white">
            <slot name="header"></slot>
          </div>
        </div>
        
        <!-- 内容区域 - 添加滚动 -->
        <div class="px-6 py-4 overflow-y-auto flex-grow">
          <div>
            <slot name="default"></slot>
          </div>
        </div>
        
        <!-- 底部按钮区域 -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <slot name="footer"></slot>
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

<style scoped>
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
