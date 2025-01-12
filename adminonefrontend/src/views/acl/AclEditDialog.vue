<template>
  <BaseDialog :show="show" @close="$emit('close')">
    <template #title>
      编辑 ACL 配置
    </template>
    
    <template #body>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span class="ml-2">加载中...</span>
      </div>
      
      <div v-else class="space-y-4">
        <!-- 用户信息（只读） -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">用户邮箱</label>
          <input
            type="text"
            :value="formData.user?.email"
            disabled
            class="w-full px-3 py-2 bg-gray-100 border rounded-md"
          />
        </div>

        <!-- 服务器选择 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">服务器</label>
          <!-- 服务器搜索框 -->
          <input
            v-model="serverSearchQuery"
            type="text"
            placeholder="搜索IP或服务器名称..."
            class="w-full px-3 py-2 border rounded-md mb-2"
          />
          <div class="max-h-40 overflow-y-auto border rounded-md p-2">
            <div v-if="availableServers.length === 0" class="text-gray-500 text-center py-2">
              暂无可用服务器
            </div>
            <div v-else v-for="server in filteredServers" 
                 :key="server.id"
                 class="flex items-center p-2 hover:bg-gray-50">
              <input
                type="radio"
                :value="server.id"
                v-model="formData.server_id"
                class="mr-2"
                name="server-selection"
              />
              <div>
                <div class="font-medium">{{ server.server_name || server.ip_address }}</div>
                <div class="text-sm text-gray-500">{{ server.ip_address }} ({{ server.region }})</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 容器选择 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">容器</label>
          <div v-if="!formData.server_id" class="text-gray-500 text-sm p-4 text-center border rounded-md">
            请先选择服务器
          </div>
          <div v-else-if="loadingContainers" class="flex justify-center items-center py-4">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span class="ml-2">加载容器列表...</span>
          </div>
          <div v-else class="max-h-40 overflow-y-auto border rounded-md p-2">
            <div v-if="serverContainers.length === 0" class="text-gray-500 text-center py-2">
              该服务器暂无可用容器
            </div>
            <div v-else v-for="container in serverContainers" 
                 :key="container.id"
                 class="flex items-center p-2 hover:bg-gray-50">
              <input
                type="radio"
                :value="container.id"
                v-model="formData.container_id"
                class="mr-2"
                name="container-selection"
              />
              <div>
                <div class="font-medium">{{ container.container_name }}</div>
                <div class="text-sm text-gray-500">
                  状态: {{ container.status }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 状态切换 -->
        <div class="form-group">
          <label class="flex items-center space-x-2">
            <input
              type="checkbox"
              v-model="formData.is_active"
              class="form-checkbox h-4 w-4 text-blue-600"
            />
            <span class="text-sm font-medium">启用此 ACL</span>
          </label>
        </div>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          color="info"
          label="取消"
          @click="$emit('close')"
        />
        <BaseButton
          color="success"
          label="保存"
          :loading="submitting"
          @click="handleSubmit"
        />
      </div>
    </template>
  </BaseDialog>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from 'vue'
import BaseDialog from '@/components/BaseDialog.vue'
import BaseButton from '@/components/BaseButton.vue'
import api from '@/services/api'

const props = defineProps({
  show: Boolean,
  aclData: Object
})

const emit = defineEmits(['close', 'submit'])

const loading = ref(false)
const submitting = ref(false)
const loadingContainers = ref(false)
const availableServers = ref([])
const serverContainers = ref([])
const serverSearchQuery = ref('')

const formData = ref({
  id: null,
  user: null,
  server_id: null,
  container_id: null,
  is_active: true
})

// 过滤服务器列表
const filteredServers = computed(() => {
  const query = serverSearchQuery.value.toLowerCase()
  return availableServers.value.filter(server => 
    server.ip_address.toLowerCase().includes(query) ||
    server.server_name.toLowerCase().includes(query)
  )
})

// 初始化表单数据
const initFormData = () => {
  console.log('初始化表单数据, aclData:', props.aclData)
  if (props.aclData) {
    formData.value = {
      id: props.aclData.id,
      user: props.aclData.user,
      server_id: props.aclData.server_id || props.aclData.servers?.[0]?.id || null,
      container_id: props.aclData.container_id || props.aclData.containers?.[0]?.container_name || null,
      is_active: props.aclData.is_active
    }
    console.log('初始化后的表单数据:', formData.value)
    console.log('用户信息:', formData.value.user)
    if (formData.value.server_id) {
      fetchServerContainers(formData.value.server_id)
    }
  }
}

// 获取服务器列表
const fetchServers = async () => {
  try {
    loading.value = true
    console.log('正在获取服务器列表...')
    const response = await api.getServers()
    console.log('服务器列表响应:', response)
    if (response.success) {
      availableServers.value = response.servers
      console.log('可用服务器:', availableServers.value)
    } else {
      throw new Error(response.message || '获取服务器列表失败')
    }
  } catch (error) {
    console.error('获取服务器列表失败:', error)
    alert('获取服务器列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取服务器的容器列表
const fetchServerContainers = async (serverId) => {
  if (!serverId) return
  try {
    loadingContainers.value = true
    console.log('正在获取容器列表, serverId:', serverId)
    const response = await api.getServerContainers(serverId)
    console.log('容器列表响应:', response)
    if (!response || typeof response !== 'object') {
      throw new Error('Invalid response format')
    }
    if (response.success) {
      if (!Array.isArray(response.containers)) {
        throw new Error('Invalid containers data format')
      }
      // 过滤出属于当前服务器的容器
      serverContainers.value = response.containers.filter(container => 
        container.server_id === serverId
      )
      console.log('服务器容器:', serverContainers.value)
    } else {
      throw new Error(response.message || '获取容器列表失败')
    }
  } catch (error) {
    console.error('获取容器列表失败:', error)
    alert('获取容器列表失败: ' + error.message)
    serverContainers.value = []
  } finally {
    loadingContainers.value = false
  }
}

// 监听服务器选择变化
watch(() => formData.value.server_id, (newServerId) => {
  formData.value.container_id = null // 清空容器选择
  if (newServerId) {
    console.log('服务器选择变化，获取对应容器列表:', newServerId)
    fetchServerContainers(newServerId)
  } else {
    serverContainers.value = []
  }
})

// 提交表单
const handleSubmit = async () => {
  if (!formData.value.server_id || !formData.value.container_id) {
    alert('请选择服务器和容器')
    return
  }

  if (!formData.value.user?.id) {
    alert('用户信息不完整')
    return
  }

  console.log('提交的表单数据:', formData.value)

  try {
    submitting.value = true
    // 构造请求数据
    const requestData = {
      user_id: formData.value.user.id,
      server_id: formData.value.server_id,
      container_ids: [parseInt(formData.value.container_id)],
      is_active: formData.value.is_active
    }
    
    console.log('发送到后端的数据:', requestData)

    const response = await api.generateAcl(requestData)
    
    if (response.success) {
      console.log('ACL生成成功')
      console.log('服务器响应:', response)
      emit('submit')
      emit('close')
    } else {
      throw new Error(response.message || '生成ACL失败')
    }
  } catch (error) {
    console.error('生成ACL失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      alert('生成ACL失败: ' + (error.response.data.message || error.message))
    } else {
      console.error('错误详情:', error)
      alert('生成ACL失败: ' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 监听对话框显示状态
watch(() => props.show, (newVal) => {
  console.log('对话框显示状态变化:', newVal)
  if (newVal) {
    serverSearchQuery.value = ''
    initFormData()
    fetchServers()
  } else {
    // 清理数据
    availableServers.value = []
    serverContainers.value = []
    formData.value = {
      id: null,
      user: null,
      server_id: null,
      container_id: null,
      is_active: true
    }
  }
})

// 组件卸载时清理
onUnmounted(() => {
  availableServers.value = []
  serverContainers.value = []
})
</script>

<style scoped>
.form-group {
  @apply mb-4;
}

.form-checkbox {
  @apply rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50;
}

input[type="radio"] {
  @apply w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500;
}
</style> 