<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseDialog from '@/components/BaseDialog.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { mdiInformation } from '@mdi/js'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close', 'create'])

// 表单数据
const rentalForm = ref({
  serial_code: '',
  user_id: '',
  traffic_limit: 0,
  server_id: null, // 改为 null，需要用户选择
  container_config: {
    cpu_limit: 1,
    memory_limit: 1024,
    bandwidth_limit: 100
  }
})

// 添加服务器列表
const servers = ref([])

// 获取服务器列表
const fetchServers = async () => {
  try {
    const response = await api.getServers()
    if (response.success) {
      servers.value = response.servers
    }
  } catch (error) {
    console.error('获取服务器列表失败:', error)
  }
}

// 在组件挂载时获取服务器列表
onMounted(() => {
  fetchServers()
})

// 表单验证规则
const rules = {
  serial_code: [
    v => !!v || '序列号是必填项',
    v => /^[A-Z0-9]{8,}$/.test(v) || '序列号格式不正确'
  ],
  user_id: [
    v => !!v || '用户ID是必填项',
    v => !isNaN(v) || '用户ID必须是数字'
  ],
  traffic_limit: [
    v => v >= 0 || '流量限制不能为负数',
    v => v <= 10000 || '流量限制不能超过10000GB'
  ],
  server_id: [
    v => !!v || '请选择服务器'
  ]
}

// 验证错误信息
const errors = ref({})

// 验证表单
const validateForm = () => {
  errors.value = {}
  let isValid = true

  // 验证每个字段
  Object.keys(rules).forEach(field => {
    const fieldRules = rules[field]
    const value = rentalForm.value[field]

    for (const rule of fieldRules) {
      const result = rule(value)
      if (result !== true) {
        errors.value[field] = result
        isValid = false
        break
      }
    }
  })

  return isValid
}

// 处理创建
const handleCreate = async () => {
  if (!validateForm()) return

  try {
    emit('create', {
      ...rentalForm.value,
      // 添加其他必要的配置
      container_config: {
        ...rentalForm.value.container_config,
        name: `container_${rentalForm.value.user_id}`,
        image: 'default_image:latest'
      }
    })
  } catch (error) {
    console.error('创建租赁失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  rentalForm.value = {
    serial_code: '',
    user_id: '',
    traffic_limit: 0,
    server_id: null,
    container_config: {
      cpu_limit: 1,
      memory_limit: 1024,
      bandwidth_limit: 100
    }
  }
  errors.value = {}
}

// 监听对话框关闭
const handleClose = () => {
  resetForm()
  emit('close')
}

// 添加调试
console.log('RentalCreateDialog mounted')
</script>

<template>
  <BaseDialog
    :show="show"
    @close="handleClose"
    :max-width="600"
  >
    <template #header>
      <div class="text-lg font-bold">创建租赁</div>
    </template>

    <template #default>
      <div class="grid gap-4">
        <!-- 基本信息 -->
        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4">
          <div class="flex items-center text-blue-700 dark:text-blue-300 mb-2">
            <BaseIcon :path="mdiInformation" class="mr-2" />
            <span class="font-medium">创建说明</span>
          </div>
          <p class="text-sm text-blue-600 dark:text-blue-400">
            创建租赁将自动：分配服务器资源、创建容器、配置ACL规则、更新流量限制。
          </p>
        </div>

        <!-- 必填信息 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">
            序列号 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="rentalForm.serial_code"
            type="text"
            class="form-input"
            :class="{'border-red-500': errors.serial_code}"
            placeholder="请输入序列号"
          />
          <span v-if="errors.serial_code" class="text-red-500 text-xs mt-1">
            {{ errors.serial_code }}
          </span>
        </div>

        <div class="form-group">
          <label class="block text-sm font-medium mb-2">
            用户ID <span class="text-red-500">*</span>
          </label>
          <input
            v-model="rentalForm.user_id"
            type="text"
            class="form-input"
            :class="{'border-red-500': errors.user_id}"
            placeholder="请输入用户ID"
          />
          <span v-if="errors.user_id" class="text-red-500 text-xs mt-1">
            {{ errors.user_id }}
          </span>
        </div>

        <div class="form-group">
          <label class="block text-sm font-medium mb-2">
            流量限制(GB)
          </label>
          <input
            v-model.number="rentalForm.traffic_limit"
            type="number"
            min="0"
            max="10000"
            class="form-input"
            :class="{'border-red-500': errors.traffic_limit}"
            placeholder="请输入流量限制"
          />
          <span v-if="errors.traffic_limit" class="text-red-500 text-xs mt-1">
            {{ errors.traffic_limit }}
          </span>
        </div>

        <!-- 服务器选择 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">
            选择服务器 <span class="text-red-500">*</span>
          </label>
          <select
            v-model="rentalForm.server_id"
            class="form-input"
            :class="{'border-red-500': errors.server_id}"
          >
            <option value="">请选择服务器</option>
            <option
              v-for="server in servers"
              :key="server.id"
              :value="server.id"
            >
              {{ server.name }} ({{ server.ip }}) - 剩余流量: {{ server.remaining_traffic }}GB
            </option>
          </select>
          <span v-if="errors.server_id" class="text-red-500 text-xs mt-1">
            {{ errors.server_id }}
          </span>
        </div>

        <!-- 容器配置 -->
        <details class="mt-4" v-if="rentalForm.server_id">
          <summary class="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
            容器配置（可选）
          </summary>
          <div class="mt-3 grid gap-4">
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">CPU 限制 (核)</label>
              <input
                v-model.number="rentalForm.container_config.cpu_limit"
                type="number"
                min="0.1"
                step="0.1"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">内存限制 (MB)</label>
              <input
                v-model.number="rentalForm.container_config.memory_limit"
                type="number"
                min="128"
                step="128"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">带宽限制 (Mbps)</label>
              <input
                v-model.number="rentalForm.container_config.bandwidth_limit"
                type="number"
                min="1"
                class="form-input"
              />
            </div>
          </div>
        </details>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          color="info"
          label="取消"
          @click="handleClose"
        />
        <BaseButton
          color="success"
          label="创建"
          @click="handleCreate"
        />
      </div>
    </template>
  </BaseDialog>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

.form-input {
  @apply w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}

details summary::-webkit-details-marker {
  display: none;
}

details summary::before {
  content: '▸';
  display: inline-block;
  margin-right: 0.5rem;
  transition: transform 0.2s;
}

details[open] summary::before {
  transform: rotate(90deg);
}

details summary {
  @apply flex items-center hover:text-blue-600 transition-colors duration-200;
}
</style> 