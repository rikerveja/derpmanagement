<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiDocker,
  mdiPlus,
  mdiDelete,
  mdiServerPlus
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import api from '@/services/api'

const router = useRouter()
const servers = ref([]) // 服务器列表
const serverSearchQuery = ref('') // 服务器搜索关键词
const existingContainers = ref([]) // 用于存储已存在的容器列表

// 容器表单数据列表
const containerForms = ref([{
  container_id: '',
  container_name: '',
  server_id: '',
  custom_id: '',
  image: 'zhangjiayuan1983/ip_derper:latest',
  port: null,
  stun_port: null,
  node_exporter_port: null,
  max_upload_traffic: 5,
  max_download_traffic: 5
}])

// 筛选后的服务器列表
const filteredServers = computed(() => {
  if (!serverSearchQuery.value) return servers.value
  const query = serverSearchQuery.value.toLowerCase()
  return servers.value.filter(server => 
    server.server_name.toLowerCase().includes(query) ||
    server.ip_address.toLowerCase().includes(query)
  )
})

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

// 获取已存在的容器列表
const fetchExistingContainers = async () => {
  try {
    const response = await api.getContainers()
    if (response.success) {
      existingContainers.value = response.containers
    }
  } catch (error) {
    console.error('获取容器列表失败:', error)
  }
}

// 添加新的容器表单
const addContainerForm = () => {
  if (containerForms.value.length < 4) {
    containerForms.value.push({
      container_id: '',
      container_name: '',
      server_id: '',
      custom_id: '',
      image: 'zhangjiayuan1983/ip_derper:latest',
      port: null,
      stun_port: null,
      node_exporter_port: null,
      max_upload_traffic: 5,
      max_download_traffic: 5
    })
  }
}

// 删除容器表单
const removeContainerForm = (index) => {
  containerForms.value.splice(index, 1)
}

// 根据服务器IP生成容器名称
const updateContainerName = (form, index) => {
  const server = servers.value.find(s => s.id === form.server_id)
  if (server && server.ip_address) {
    if (!form.container_name) {
      form.container_name = `${server.ip_address.replace(/\./g, '_')}_derp${index + 1}`
    }
  }
}

// 监听服务器选择变化
const handleServerChange = (form, index) => {
  updateContainerName(form, index)
  updateContainerId(form)
}

// 更新容器ID
const updateContainerId = (form) => {
  const server = servers.value.find(s => s.id === form.server_id)
  if (server && server.ip_address) {
    const ipPart = server.ip_address.replace(/\./g, '_')
    form.container_id = form.custom_id ? `${ipPart}_${form.custom_id}` : ''
  }
}

// 监听自定义ID变化
const handleCustomIdChange = (form) => {
  updateContainerId(form)
}

// 检查容器名称是否重复
const isContainerNameDuplicate = (name) => {
  return existingContainers.value.some(container => container.container_name === name) ||
         containerForms.value.filter(form => form.container_name === name).length > 1
}

// 检查容器ID是否重复
const isContainerIdDuplicate = (id) => {
  return existingContainers.value.some(container => container.container_id === id) ||
         containerForms.value.filter(form => form.container_id === id).length > 1
}

// 创建容器
const createContainers = async () => {
  try {
    // 检查所有表单的容器名称和ID是否重复
    for (const form of containerForms.value) {
      if (isContainerNameDuplicate(form.container_name)) {
        throw new Error(`容器名称 ${form.container_name} 已存在`)
      }
      if (isContainerIdDuplicate(form.container_id)) {
        throw new Error(`容器ID ${form.container_id} 已存在`)
      }
    }

    for (const form of containerForms.value) {
      const response = await api.createContainer(form)
      if (!response.success) {
        throw new Error(`容器 ${form.container_name} 创建失败: ${response.message}`)
      }
    }
    alert('所有容器创建成功!')
    router.push('/containers')
  } catch (error) {
    console.error('创建容器失败:', error)
    alert(error.message)
  }
}

onMounted(async () => {
  await fetchServers()
  await fetchExistingContainers()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiDocker" title="新建容器" main>
        <BaseButton
          color="info"
          label="返回列表"
          to="/containers"
        />
      </SectionTitleLineWithButton>

      <CardBox is-form @submit.prevent="createContainers">
        <div v-for="(form, index) in containerForms" :key="index" class="mb-8 pb-8 border-b border-gray-200 last:border-0">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium">容器 #{{ index + 1 }}</h3>
            <BaseButton
              v-if="containerForms.length > 1"
              :icon="mdiDelete"
              color="danger"
              small
              @click="removeContainerForm(index)"
              title="删除此容器"
            />
          </div>

          <div class="grid grid-cols-1 gap-6">
            <!-- 基本信息 -->
            <div class="space-y-4">
              <div class="form-group">
                <label class="block text-sm font-medium mb-2">容器ID号 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.custom_id"
                  type="text"
                  required
                  placeholder="请输入容器ID号（如：1、2、3等）"
                  class="w-full px-3 py-2 border rounded-md"
                  @input="handleCustomIdChange(form)"
                >
                <div class="mt-1 text-sm text-gray-500">
                  最终容器ID: {{ form.container_id || '未生成' }}
                </div>
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">容器名称 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.container_name"
                  type="text"
                  required
                  placeholder="可自定义，默认根据服务器IP自动生成"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">选择服务器 <span class="text-red-500">*</span></label>
                <div class="space-y-2">
                  <input
                    v-model="serverSearchQuery"
                    type="text"
                    placeholder="搜索服务器名称或IP..."
                    class="w-full px-3 py-2 border rounded-md"
                  >
                  <select
                    v-model="form.server_id"
                    required
                    class="w-full px-3 py-2 border rounded-md"
                    size="3"
                    @change="handleServerChange(form, index)"
                  >
                    <option v-for="server in filteredServers" :key="server.id" :value="server.id">
                      {{ server.server_name }} ({{ server.ip_address }})
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">镜像 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.image"
                  type="text"
                  required
                  placeholder="zhangjiayuan1983/ip_derper:latest"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>
            </div>

            <!-- 端口配置 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="form-group">
                <label class="block text-sm font-medium mb-2">DERP端口 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.port"
                  type="number"
                  required
                  placeholder="DERP端口"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">STUN端口 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.stun_port"
                  type="number"
                  required
                  placeholder="STUN端口"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">NODE端口 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.node_exporter_port"
                  type="number"
                  required
                  placeholder="NODE端口"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>
            </div>

            <!-- 流量限制 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-group">
                <label class="block text-sm font-medium mb-2">上传流量限制(GB) <span class="text-red-500">*</span></label>
                <input
                  v-model="form.max_upload_traffic"
                  type="number"
                  required
                  step="0.01"
                  placeholder="默认5GB"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">下载流量限制(GB) <span class="text-red-500">*</span></label>
                <input
                  v-model="form.max_download_traffic"
                  type="number"
                  required
                  step="0.01"
                  placeholder="默认5GB"
                  class="w-full px-3 py-2 border rounded-md"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 添加容器按钮 -->
        <div class="flex justify-center mt-4" v-if="containerForms.length < 4">
          <BaseButton
            :icon="mdiServerPlus"
            color="success"
            @click="addContainerForm"
            label="添加新容器"
          />
        </div>

        <template #footer>
          <BaseButtons>
            <BaseButton
              type="submit"
              color="info"
              label="创建容器"
              :icon="mdiPlus"
            />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}
</style> 
