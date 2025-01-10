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
  serial_number: '',
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
      serial_number: '',
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
    const formattedIp = server.ip_address.replace(/\./g, '_')
    // 如果容器名称已经包含下划线，说明已经有IP前缀，需要移除
    const originalName = form.container_name.includes('_')
      ? form.container_name.split('_').slice(-2).join('_')  // 保留 derper_N 部分
      : form.container_name
    form.container_name = `${formattedIp}_${originalName}`
  }
}

// 监听服务器选择变化
const handleServerChange = (form, index) => {
  updateContainerName(form, index)
  if (form.container_id) {
    updateContainerId(form)
  }
}

// 监听序列号变化并更新容器ID
const handleSerialNumberChange = (form) => {
  updateContainerId(form)
}

// 更新容器ID
const updateContainerId = (form) => {
  if (form.server_id) {
    const server = servers.value.find(s => s.id === form.server_id)
    if (server) {
      const formattedIp = server.ip_address.replace(/\./g, '_')
      const originalId = form.container_id.includes('_') 
        ? form.container_id.split('_').pop() 
        : form.container_id
      form.container_id = `${formattedIp}_${originalId}`
    }
  }
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
      // 获取服务器信息用于检查
      const server = servers.value.find(s => s.id === form.server_id)
      if (!server) {
        throw new Error('未找到对应的服务器信息')
      }
      
      if (isContainerNameDuplicate(form.container_name)) {
        throw new Error(`容器名称 ${form.container_name} 已存在`)
      }
      if (isContainerIdDuplicate(form.container_id)) {
        throw new Error(`容器ID ${form.container_id} 已存在`)
      }
    }

    for (const form of containerForms.value) {
      // 构造发送到API的数据
      const containerData = {
        ...form,
        container_id: form.container_id,
        container_name: form.container_name,
      }
      
      console.log('提交的容器数据:', containerData)
      
      const response = await api.createContainer(containerData)
      if (!response.success) {
        throw new Error(`容器 ${containerData.container_name} 创建失败: ${response.message}`)
      }
    }
    alert('所有容器创建成功!')
    router.push('/containers')
  } catch (error) {
    console.error('创建容器失败:', error)
    alert(error.message)
  }
}

// 批量解析相关的状态
const dockerOutput = ref('')

// 解析 docker ps 输出的函数
const parseDockerOutput = () => {
  const output = dockerOutput.value
  if (!output) return

  // 正则表达式
  const containerIdRegex = /^([a-f0-9]{12})/gm
  const containerNameRegex = /\s+(derper_[1-4])\s*$/gm
  const derpPortRegex = /0\.0\.0\.0:(\d+)->443\/tcp/g
  const stunPortRegex = /0\.0\.0\.0:(\d+)->3478\/udp/g
  const nodePortRegex = /0\.0\.0\.0:(\d+)->9100\/tcp/g

  // 提取数据
  const containerIds = [...output.matchAll(containerIdRegex)].map(match => match[1])
  const containerNames = [...output.matchAll(containerNameRegex)].map(match => match[1])
  const derpPorts = [...output.matchAll(derpPortRegex)].map(match => match[1])
  const stunPorts = [...output.matchAll(stunPortRegex)].map(match => match[1])
  const nodePorts = [...output.matchAll(nodePortRegex)].map(match => match[1])

  // 清空现有表单
  containerForms.value = []

  // 根据解析结果创建表单，保持原始顺序
  containerNames.forEach((name, index) => {
    containerForms.value.push({
      container_id: containerIds[index] || '',
      container_name: name.trim(),  // 确保名称没有多余空格
      server_id: '',
      serial_number: '',
      image: 'zhangjiayuan1983/ip_derper:latest',
      port: parseInt(derpPorts[index]) || null,
      stun_port: parseInt(stunPorts[index]) || null,
      node_exporter_port: parseInt(nodePorts[index]) || null,
      max_upload_traffic: 5,
      max_download_traffic: 5
    })
  })
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

      <!-- 批量解析区域 -->
      <CardBox class="mb-6">
        <div class="space-y-4">
          <div class="form-group">
            <label class="block text-lg font-medium mb-2">
              批量解析 Docker PS 输出
              <span class="text-sm font-normal text-gray-500 ml-2">
                (粘贴 docker ps 命令输出进行批量解析)
              </span>
            </label>
            <textarea
              v-model="dockerOutput"
              rows="12"
              class="w-full px-3 py-2 border rounded-md font-mono text-sm"
              style="min-height: 300px; font-size: 16px; line-height: 1.5;"
              placeholder="请粘贴 docker ps 命令的完整输出..."
              :class="[
                'transition-all duration-200',
                'focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'dark:bg-gray-800 dark:text-gray-100',
                'resize-y'
              ]"
            ></textarea>
          </div>
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-500">
              提示：粘贴完整的 docker ps 命令输出，包含 CONTAINER ID、PORTS、NAMES 等信息
            </div>
            <BaseButton
              color="success"
              label="解析数据"
              :icon="mdiPlus"
              @click="parseDockerOutput"
              class="px-6 py-2 text-lg"
            />
          </div>
        </div>
      </CardBox>

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
                <label class="block text-sm font-medium mb-2">容器ID <span class="text-red-500">*</span></label>
                <input
                  v-model="form.container_id"
                  type="text"
                  required
                  placeholder="容器ID"
                  class="w-full px-3 py-2 border rounded-md"
                  @input="handleServerChange(form, index)"
                >
                <div class="mt-1 text-sm text-gray-500">
                  当选择服务器后，会自动在容器ID前添加服务器IP
                </div>
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium mb-2">容器名称 <span class="text-red-500">*</span></label>
                <input
                  v-model="form.container_name"
                  type="text"
                  required
                  placeholder="默认根据序号自动生成"
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
