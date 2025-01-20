<script setup>
import { ref, computed, onMounted } from 'vue'
import { useServerStore } from '@/stores/servers'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiDocker,
  mdiPlus,
  mdiDelete,
  mdiRefresh,
  mdiPencil,
  mdiStop,
  mdiPlay,
  mdiOpenInNew
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseDialog from '@/components/BaseDialog.vue'
import api from '@/services/api'

const containers = ref([])
const serverStore = useServerStore()
const currentPage = ref(1)
const itemsPerPage = 10
const searchQuery = ref('')
const selectedStatus = ref('all')

// 编辑对话框状态
const showEditDialog = ref(false)
const editContainerForm = ref({
  container_id: '',
  container_name: '',
  image: '',
  port: null,
  stun_port: null,
  node_exporter_port: null,
  max_upload_traffic: 5,
  max_download_traffic: 5
})

// 编辑容器
const editContainer = async (container) => {
  try {
    // 直接使用传入的容器数据
    editContainerForm.value = {
      container_id: container.container_id,
      container_name: container.container_name,
      image: container.image,
      port: container.port,
      stun_port: container.stun_port,
      node_exporter_port: container.node_exporter_port,
      max_upload_traffic: container.max_upload_traffic,
      max_download_traffic: container.max_download_traffic
    }
    showEditDialog.value = true
  } catch (error) {
    console.error('获取容器详情失败:', error)
  }
}

// 更新容器
const updateContainer = async () => {
  try {
    console.log('正在更新容器:', editContainerForm.value)
    const response = await api.updateContainer(editContainerForm.value.container_name, {
      new_image: editContainerForm.value.image,
      ports: {
        derp_port: editContainerForm.value.port,
        stun_port: editContainerForm.value.stun_port,
        node_port: editContainerForm.value.node_exporter_port
      },
      environment: {
        max_upload_traffic: editContainerForm.value.max_upload_traffic,
        max_download_traffic: editContainerForm.value.max_download_traffic
      }
    })
    
    if (response.success) {
      alert('更新成功!')
      showEditDialog.value = false
      await fetchContainers() // 刷新容器列表
    } else {
      alert('更新失败: ' + response.message)
    }
  } catch (error) {
    console.error('更新容器失败:', error)
    alert('更新失败: ' + error.message)
  }
}

// 获取容器列表
const fetchContainers = async () => {
  try {
    const response = await api.getContainers()
    console.log('容器列表响应:', response)
    if (response.success) {
      containers.value = response.containers
      console.log('容器列表:', containers.value)
      await fetchServerDetails()
      console.log('服务器详情:', serverStore.servers)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取容器列表失败:', error)
    containers.value = []
  }
}

// 获取服务器详细信息
const fetchServerDetails = async () => {
  try {
    // 获取所有不重复的服务器ID
    const serverIds = [...new Set(containers.value.map(c => c.server_id))]
    console.log('需要获取详情的服务器IDs:', serverIds)
    
    // 并行获取所有服务器的状态信息
    const promises = serverIds.map(async (serverId) => {
      try {
        const response = await serverStore.fetchServerDetails(serverId)
        console.log(`服务器 ${serverId} 的响应:`, response)
      } catch (error) {
        console.error(`获取服务器 ${serverId} 状态失败:`, error)
      }
    })
    
    await Promise.all(promises)
    console.log('所有服务器详情:', serverStore.servers)
  } catch (error) {
    console.error('获取服务器详细信息失败:', error)
  }
}

// 获取服务器信息的计算属性
const getServerInfo = (serverId) => {
  console.log('开始获取服务器信息:', serverId)
  console.log(`获取服务器 ${serverId} 的信息, 当前缓存:`, serverStore.servers[serverId])
  const server = serverStore.servers[serverId]
  if (!server) {
    console.warn(`未找到服务器 ${serverId} 的信息`)
    return { name: '未知服务器', ip: '未知IP' }
  }
  const result = {
    name: server.server_name || '未知服务器',
    ip: server.ip_address || '未知IP'
  }
  console.log('返回服务器信息:', result)
  return result
}

// 停止容器
const stopContainer = async (containerId) => {
  try {
    const response = await api.stopContainer(containerId)
    if (response.success) {
      await fetchContainers()
    }
  } catch (error) {
    console.error('停止容器失败:', error)
  }
}

// 启动容器
const startContainer = async (containerId) => {
  try {
    const response = await api.startContainer(containerId)
    if (response.success) {
      await fetchContainers()
    }
  } catch (error) {
    console.error('启动容器失败:', error)
  }
}

// 删除容器
const deleteContainer = async (containerId) => {
  if (confirm('确定要删除此容器吗？')) {
    try {
      const response = await api.deleteContainer(containerId)
      if (response.success) {
        await fetchContainers()
      }
    } catch (error) {
      console.error('删除容器失败:', error)
    }
  }
}

// 筛选后的容器列表
const filteredContainers = computed(() => {
  return containers.value.filter(container => {
    const matchesSearch = searchQuery.value === '' || 
      container.container_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      container.container_id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (container.server?.server_name || '').toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = selectedStatus.value === 'all' || container.status === selectedStatus.value
    return matchesSearch && matchesStatus
  })
})

// 分页后的容器列表
const paginatedContainers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredContainers.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredContainers.value.length / itemsPerPage)
})

// 格式化状态显示
const getStatusClass = (status) => {
  const classes = {
    'px-2 py-1 rounded text-xs font-medium': true,
    'bg-green-100 text-green-800': status === 'running',
    'bg-red-100 text-red-800': status === 'stopped' || status === 'exited',
    'bg-yellow-100 text-yellow-800': status === 'paused' || status === 'restarting'
  }
  return classes
}

// 格式化时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '未知时间'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch (error) {
    console.error('时间格式化失败:', error)
    return dateStr
  }
}

// 从容器名称中提取 IP 地址
const extractIpFromContainerName = (containerName) => {
  if (!containerName) return '-'
  const parts = containerName.split('_')
  if (parts.length >= 4) {
    return parts.slice(0, 4).join('.')
  }
  return '-'
}

onMounted(async () => {
  await fetchContainers()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiDocker" title="容器列表" main>
        <BaseButton
          :icon="mdiPlus"
          color="info"
          label="新建容器"
          to="/containers/add"
        />
      </SectionTitleLineWithButton>

      <CardBox>
        <!-- 筛选工具栏 -->
        <div class="flex flex-wrap gap-3 mb-3">
          <div class="flex-1 min-w-[200px]">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索容器名称、ID或服务器..."
              class="w-full px-2 py-1 border rounded-md text-sm"
            >
          </div>
          <select
            v-model="selectedStatus"
            class="px-2 py-1 border rounded-md text-sm"
          >
            <option value="all">全部状态</option>
            <option value="running">运行中</option>
          </select>
          <BaseButton
            :icon="mdiRefresh"
            color="info"
            small
            @click="fetchContainers"
            title="刷新列表"
          />
        </div>

        <!-- 容器列表表格 -->
        <div class="overflow-hidden">
          <table class="w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">
                  容器名称
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-36">
                  服务器IP
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">
                  端口信息
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                  状态
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                  流量限制
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                  已用流量
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-36">
                  创建时间
                </th>
                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="container in paginatedContainers" :key="container.id" 
                  class="hover:bg-gray-50">
                <td class="px-4 py-2 whitespace-nowrap">
                  <div class="flex items-center">
                    <BaseIcon :path="mdiDocker" class="flex-shrink-0 h-4 w-4 text-gray-400 mr-2"/>
                    <div class="text-sm font-medium text-gray-900 truncate max-w-[180px]" :title="container.container_name">
                      {{ container.container_name }}
                    </div>
                  </div>
                </td>
                <td class="px-4 py-2 whitespace-nowrap font-mono text-sm text-gray-600">
                  <a 
                    :href="`https://${extractIpFromContainerName(container.container_name)}:${container.port}`"
                    target="_blank"
                    class="text-blue-600 hover:text-blue-800 hover:underline"
                    :title="'打开 Node Exporter 页面'"
                  >
                    {{ extractIpFromContainerName(container.container_name) }}
                    <BaseIcon 
                      :path="mdiOpenInNew" 
                      class="inline-block w-4 h-4 ml-1" 
                    />
                  </a>
                </td>
                <td class="px-4 py-2 whitespace-nowrap">
                  <div class="flex flex-col space-y-0.5 text-sm">
                    <div class="grid grid-cols-[60px,1fr]">
                      <span class="text-gray-500">DERP:</span>
                      <span>{{ container.port }}</span>
                    </div>
                    <div class="grid grid-cols-[60px,1fr]">
                      <span class="text-gray-500">STUN:</span>
                      <span>{{ container.stun_port }}</span>
                    </div>
                    <div class="grid grid-cols-[60px,1fr]">
                      <span class="text-gray-500">NODE:</span>
                      <span>{{ container.node_exporter_port }}</span>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-2 whitespace-nowrap">
                  <span :class="getStatusClass(container.status)">
                    <template v-if="container.status === 'running'">
                      <a 
                        :href="`http://${extractIpFromContainerName(container.container_name)}:${container.node_exporter_port}`"
                        target="_blank"
                        class="text-green-600 hover:text-green-800 hover:underline inline-flex items-center"
                      >
                        {{ container.status }}
                        <BaseIcon
                          :path="mdiOpenInNew"
                          size="16"
                          class="ml-1"
                        />
                      </a>
                    </template>
                    <template v-else>
                      {{ container.status }}
                    </template>
                  </span>
                </td>
                <td class="px-4 py-2 whitespace-nowrap">
                  <div class="flex flex-col space-y-1 text-sm">
                    <div class="grid grid-cols-[60px,1fr]">
                      <span class="text-gray-500">上传:</span>
                      <span>{{ container.max_upload_traffic }}</span>
                    </div>
                    <div class="grid grid-cols-[60px,1fr]">
                      <span class="text-gray-500">下载:</span>
                      <span>{{ container.max_download_traffic }}</span>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-2 whitespace-nowrap">
                  <div class="flex flex-col space-y-2">
                    <span class="text-sm">{{ container.upload_traffic || '0' }} GB</span>
                    <div class="w-full bg-gray-200 rounded h-2">
                      <div 
                        class="bg-blue-600 h-2 rounded" 
                        :style="{
                          width: `${((container.upload_traffic || 0) / container.max_upload_traffic * 100)}%`
                        }"
                        :class="{
                          'bg-yellow-500': (container.upload_traffic || 0) > container.max_upload_traffic * 0.8,
                          'bg-red-500': (container.upload_traffic || 0) > container.max_upload_traffic * 0.95
                        }"
                      ></div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDateTime(container.created_at) }}
                </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <BaseButton
                      :icon="container.status === 'running' ? mdiStop : mdiPlay"
                      :color="container.status === 'running' ? 'danger' : 'success'"
                      small
                      @click="container.status === 'running' ? 
                        stopContainer(container.container_id) : 
                        startContainer(container.container_id)"
                      :title="container.status === 'running' ? '停止' : '启动'"
                    />
                    <BaseButton
                      :icon="mdiPencil"
                      color="info"
                      small
                      @click="editContainer(container)"
                      title="编辑"
                    />
                    <BaseButton
                      :icon="mdiDelete"
                      color="danger"
                      small
                      @click="deleteContainer(container.container_id)"
                      title="删除"
                    />
                  </div>
                </td>
              </tr>
              <tr v-if="paginatedContainers.length === 0">
                <td colspan="8" class="px-4 py-8 text-center text-gray-500">
                  暂无容器数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="mt-3 flex items-center justify-between text-sm">
          <div class="text-gray-700">
            显示 {{ (currentPage - 1) * itemsPerPage + 1 }} 到 
            {{ Math.min(currentPage * itemsPerPage, filteredContainers.length) }} 条，
            共 {{ filteredContainers.length }} 条
          </div>
          <div class="flex space-x-2">
            <BaseButton
              @click="currentPage--"
              :disabled="currentPage === 1"
              label="上一页"
            />
            <span class="px-4 py-2">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <BaseButton
              @click="currentPage++"
              :disabled="currentPage >= totalPages"
              label="下一页"
            />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>

  <!-- 编辑容器对话框 -->
  <BaseDialog
    v-model="showEditDialog"
    :show="showEditDialog"
    @close="showEditDialog = false"
  >
    <template #title>
      编辑容器
    </template>
    
    <template #body>
      <div class="space-y-4">
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">容器名称</label>
          <input
            v-model="editContainerForm.container_name"
            type="text"
            class="w-full px-3 py-2 border rounded-md"
            disabled
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">镜像</label>
          <input
            v-model="editContainerForm.image"
            type="text"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">DERP端口</label>
          <input
            v-model="editContainerForm.port"
            type="number"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">STUN端口</label>
          <input
            v-model="editContainerForm.stun_port"
            type="number"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">NODE端口</label>
          <input
            v-model="editContainerForm.node_exporter_port"
            type="number"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">上传流量限制(GB)</label>
          <input
            v-model="editContainerForm.max_upload_traffic"
            type="number"
            step="0.01"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">下载流量限制(GB)</label>
          <input
            v-model="editContainerForm.max_download_traffic"
            type="number"
            step="0.01"
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          color="info"
          label="取消"
          @click="showEditDialog = false"
        />
        <BaseButton
          color="success"
          label="保存"
          @click="updateContainer"
        />
      </div>
    </template>
  </BaseDialog>
</template> 
