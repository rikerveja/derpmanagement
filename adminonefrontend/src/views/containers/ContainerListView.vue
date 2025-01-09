<script setup>
import { ref, computed, onMounted } from 'vue'
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
  mdiPlay
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

const containers = ref([])
const serverDetails = ref({})
const currentPage = ref(1)
const itemsPerPage = 10
const searchQuery = ref('')
const selectedStatus = ref('all')

// 获取容器列表
const fetchContainers = async () => {
  try {
    const response = await api.getContainers()
    console.log('容器列表响应:', response)
    if (response.success) {
      containers.value = response.containers
      console.log('容器列表:', containers.value)
      await fetchServerDetails()
      console.log('服务器详情:', serverDetails.value)
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
    
    // 并行获取所有服务器的状态信息
    const promises = serverIds.map(async (serverId) => {
      try {
        // 通过server_id获取服务器信息
        const response = await api.getServer(serverId)  // 修改为正确的API调用
        if (response && response.success) {
          serverDetails.value[serverId] = response.server
        } else {
          console.error('获取服务器信息失败:', serverId, response)
        }
      } catch (error) {
        console.error(`获取服务器 ${serverId} 状态失败:`, error)
      }
    })
    
    await Promise.all(promises)
  } catch (error) {
    console.error('获取服务器详细信息失败:', error)
  }
}

// 获取服务器信息的计算属性
const getServerInfo = (serverId) => {
  const server = serverDetails.value[serverId]
  if (!server) return { name: '未知服务器', ip: '未知IP' }
  return {
    name: server.hostname || '未知服务器',  // 使用正确的字段名
    ip: server.ip_address || '未知IP'      // 使用正确的字段名
  }
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

// 编辑容器
const editContainer = (container) => {
  router.push(`/containers/${container.id}/edit`)
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
        <div class="flex flex-wrap gap-4 mb-4">
          <div class="flex-1 min-w-[200px]">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索容器名称、ID或服务器..."
              class="w-full px-3 py-2 border rounded-md"
            >
          </div>
          <select
            v-model="selectedStatus"
            class="px-3 py-2 border rounded-md"
          >
            <option value="all">全部状态</option>
            <option value="running">运行中</option>
            <option value="stopped">已停止</option>
            <option value="paused">已暂停</option>
            <option value="restarting">重启中</option>
            <option value="exited">已退出</option>
          </select>
          <BaseButton
            :icon="mdiRefresh"
            color="info"
            @click="fetchContainers"
            title="刷新列表"
          />
        </div>

        <!-- 容器列表表格 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">容器名称</th>
                <th class="px-4 py-3 text-left">所在服务器</th>
                <th class="px-4 py-3 text-left">端口信息</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">流量限制(GB)</th>
                <th class="px-4 py-3 text-left">已用流量</th>
                <th class="px-4 py-3 text-left">创建时间</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="container in paginatedContainers" :key="container.id" 
                  class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="flex flex-col space-y-1">
                    <span class="font-medium text-sm">{{ container.container_name }}</span>
                    <span class="text-xs text-gray-500">{{ container.container_id }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-col space-y-1">
                    <span class="text-sm">{{ getServerInfo(container.server_id).name }}</span>
                    <span class="text-xs text-gray-500">{{ getServerInfo(container.server_id).ip }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-col space-y-1 text-sm">
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
                <td class="px-4 py-3">
                  <span :class="getStatusClass(container.status)">
                    {{ container.status }}
                  </span>
                </td>
                <td class="px-4 py-3">
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
                <td class="px-4 py-3">
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
                <td class="px-4 py-3 text-sm">{{ formatDateTime(container.created_at) }}</td>
                <td class="px-4 py-3">
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
        <div class="mt-4 flex items-center justify-between">
          <div class="text-sm text-gray-700">
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
</template> 
