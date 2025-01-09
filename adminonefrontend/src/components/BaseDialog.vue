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
            <slot name="title">对话框标题</slot>
          </div>
        </div>
        
        <!-- 内容区域 -->
        <div class="px-6 py-4 overflow-y-auto">
          <slot name="body">对话框内容</slot>
        </div>
        
        <!-- 底部按钮区域 -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <slot name="footer">
            <div class="flex justify-end space-x-2">
              <button 
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                @click="handleClose"
              >
                取消
              </button>
              <button 
                class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                @click="$emit('confirm')"
              >
                确定
              </button>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

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