<template>
  <div class="form-group">
    <label class="block text-sm font-medium mb-2">{{ label }} <span class="text-red-500">*</span></label>
    <div class="relative space-y-2">
      <!-- 搜索输入框 -->
      <input
        v-model="searchQuery"
        type="text"
        class="form-input pr-10"
        :placeholder="`搜索${label}...`"
        @input="handleSearch"
        @focus="showDropdown = true"
      />

      <!-- 下拉列表 -->
      <div v-if="showDropdown && filteredItems.length > 0"
           class="absolute z-50 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-y-auto">
        <div v-for="item in filteredItems"
             :key="item.id"
             class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
             @click="handleSelect(item)">
          <slot name="item" :item="item">
            {{ item.label }}
          </slot>
        </div>
      </div>

      <!-- 加载指示器 -->
      <div v-if="loading" class="absolute right-2 top-2">
        <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
    </div>
    <div v-if="error" class="mt-1 text-sm text-red-600">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 定义 props
const props = defineProps({
  label: String,
  items: Array,
  loading: Boolean,
  error: String
})

// 定义 emits
const emit = defineEmits(['select'])

const searchQuery = ref('')
const showDropdown = ref(false)

const filteredItems = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return props.items.filter(item => 
    item.label.toLowerCase().includes(query)
  )
})

const handleSearch = () => {
  showDropdown.value = true
}

const handleSelect = (item) => {
  searchQuery.value = item.label
  showDropdown.value = false
  emit('select', item)
}

// 点击外部关闭下拉列表
const closeDropdown = (e) => {
  if (!e.target.closest('.form-group')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.form-input {
  @apply w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style> 