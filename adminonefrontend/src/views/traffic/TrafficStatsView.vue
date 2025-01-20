<template>
  <div class="grid gap-6">
    <!-- 控制栏 -->
    <CardBox>
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <label class="text-gray-700 dark:text-gray-300">选择服务器:</label>
          <select 
            v-model="selectedServer"
            class="form-select rounded-md border-gray-300 shadow-sm"
            :disabled="loading"
          >
            <option value="">请选择服务器</option>
            <option 
              v-for="server in servers" 
              :key="server.id" 
              :value="server.id"
              :disabled="server.status === 'unreachable'"
            >
              {{ server.name }} ({{ server.ip_address }})
              {{ server.status === 'unreachable' ? '(不可达)' : '' }}
            </option>
          </select>

          <!-- 容器选择 -->
          <template v-if="selectedServer">
            <label class="text-gray-700 dark:text-gray-300">选择容器:</label>
            <select
              v-model="selectedContainer"
              class="form-select rounded-md border-gray-300 shadow-sm"
              :disabled="loading || loadingContainers"
            >
              <option value="">请选择容器</option>
              <option
                v-for="container in serverContainers"
                :key="container.id"
                :value="container.id"
              >
                {{ container.container_name || container.id }}
              </option>
            </select>
          </template>
        </div>
        <div class="flex space-x-2">
          <BaseButton
            color="success"
            label="保存流量数据"
            :icon="mdiContentSave"
            :loading="saving"
            @click="saveTrafficData"
            :disabled="!selectedContainer"
          />
          <BaseButton
            color="info"
            label="刷新"
            :icon="mdiRefresh"
            :loading="loading"
            @click="fetchTrafficData"
            :disabled="!selectedContainer"
          />
        </div>
      </div>
    </CardBox>

    <!-- 错误提示 -->
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <!-- 流量数据卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100 dark:bg-green-800">
            <BaseIcon :path="mdiUpload" class="w-6 h-6 text-green-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">上传流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(trafficData.upload_traffic || 0) }}
            </p>
          </div>
        </div>
      </CardBox>

      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100 dark:bg-blue-800">
            <BaseIcon :path="mdiDownload" class="w-6 h-6 text-blue-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">下载流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(trafficData.download_traffic || 0) }}
            </p>
          </div>
        </div>
      </CardBox>

      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-100 dark:bg-purple-800">
            <BaseIcon :path="mdiChartLine" class="w-6 h-6 text-purple-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">剩余流量</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(remainingTraffic) }}
            </p>
          </div>
        </div>
      </CardBox>

      <CardBox class="hover:shadow-lg transition-shadow">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-yellow-100 dark:bg-yellow-800">
            <BaseIcon :path="mdiGauge" class="w-6 h-6 text-yellow-500"/>
          </div>
          <div class="ml-4">
            <h3 class="text-gray-500 text-sm">流量限制</h3>
            <p class="text-2xl font-semibold">
              {{ formatTraffic(trafficLimit) }}
            </p>
          </div>
        </div>
      </CardBox>
    </div>

    <!-- 在流量数据卡片后面添加 -->
    <div class="mt-6">
      <CardBox>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  字段
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  原始值 (字节)
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  转换值 (MB)
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  容器ID
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500" colspan="2">
                  {{ selectedContainer ? getContainerName(selectedContainer) : '-' }}
                </td>
              </tr>
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  上传流量
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ trafficData.upload_traffic || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatTraffic(trafficData.upload_traffic || 0) }}
                </td>
              </tr>
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  下载流量
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ trafficData.download_traffic || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatTraffic(trafficData.download_traffic || 0) }}
                </td>
              </tr>
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  流量限制
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ trafficLimit }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatTraffic(trafficLimit) }}
                </td>
              </tr>
              <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  剩余流量
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ remainingTraffic }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatTraffic(remainingTraffic) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { 
  mdiUpload, 
  mdiDownload, 
  mdiChartLine,
  mdiRefresh,
  mdiContentSave,
  mdiGauge
} from '@mdi/js'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

// 状态变量
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const servers = ref([])
const selectedServer = ref('')
const selectedContainer = ref(null)
const serverContainers = ref([])
const loadingContainers = ref(false)
const trafficData = ref({})
const trafficLimit = ref(0)
const remainingTraffic = ref(0)

// 获取服务器列表
const fetchServers = async () => {
  try {
    const response = await api.getServers()
    if (response.success) {
      servers.value = response.servers
    }
  } catch (err) {
    error.value = '获取服务器列表失败'
  }
}

// 获取容器列表
const fetchContainers = async (serverId) => {
  try {
    loadingContainers.value = true
    const response = await api.getServerContainers(serverId)
    if (response.success) {
      serverContainers.value = response.containers
    }
  } catch (err) {
    error.value = '获取容器列表失败'
  } finally {
    loadingContainers.value = false
  }
}

// 获取流量数据
const fetchTrafficData = async () => {
  if (!selectedContainer.value) return
  
  try {
    loading.value = true
    error.value = ''
    
    const response = await api.getContainerTraffic(selectedContainer.value)
    if (response.success) {
      trafficData.value = response.traffic
      
      // 获取容器信息以计算剩余流量
      const container = serverContainers.value.find(c => c.id === selectedContainer.value)
      if (container) {
        // 将GB转换为字节进行计算
        const maxTrafficBytes = container.max_upload_traffic * 1024 * 1024 * 1024
        trafficLimit.value = maxTrafficBytes
        remainingTraffic.value = Math.max(0, maxTrafficBytes - (trafficData.value.upload_traffic || 0))
      }
    }
  } catch (err) {
    error.value = '获取流量数据失败'
  } finally {
    loading.value = false
  }
}

// 保存流量数据
const saveTrafficData = async () => {
  if (!selectedContainer.value || !trafficData.value) return
  
  try {
    saving.value = true
    error.value = ''
    
    // 获取容器信息以计算剩余流量
    const container = serverContainers.value.find(c => c.id === selectedContainer.value)
    if (!container) {
      throw new Error('容器信息不存在')
    }

    // 将GB转换为字节进行计算
    const maxTrafficBytes = container.max_upload_traffic * 1024 * 1024 * 1024 // GB转字节
    const uploadTrafficBytes = Math.floor(trafficData.value.upload_traffic || 0)
    const downloadTrafficBytes = Math.floor(trafficData.value.download_traffic || 0)
    const remainingBytes = Math.max(0, maxTrafficBytes - uploadTrafficBytes)
    
    const data = {
      container_id: container.container_id, // 使用原始的container_id
      upload_traffic: uploadTrafficBytes,
      download_traffic: downloadTrafficBytes,
      remaining_traffic: remainingBytes
    }
    
    console.log('准备保存的流量数据:', {
      原始数据: data,
      单位转换: {
        上传: `${(uploadTrafficBytes / (1024 * 1024)).toFixed(2)} MB`,
        下载: `${(downloadTrafficBytes / (1024 * 1024)).toFixed(2)} MB`,
        剩余: `${(remainingBytes / (1024 * 1024)).toFixed(2)} MB`,
        限制: `${container.max_upload_traffic} GB`
      }
    })
    
    const response = await api.saveTrafficData(data)
    // 成功保存
    error.value = '保存成功'
    // 刷新数据
    await fetchTrafficData()
  } catch (err) {
    error.value = err.message || '保存流量数据失败'
    console.error('保存失败:', err)
  } finally {
    saving.value = false
  }
}

// 格式化流量显示
const formatTraffic = (bytes) => {
  if (typeof bytes !== 'number') return '0.00 MB'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

// 监听服务器选择变化
watch(selectedServer, async (newServerId) => {
  selectedContainer.value = null
  trafficData.value = {}
  if (newServerId) {
    await fetchContainers(newServerId)
  }
})

// 监听容器选择变化
watch(selectedContainer, async (newContainerId) => {
  if (newContainerId) {
    await fetchTrafficData()
  } else {
    trafficData.value = {}
  }
})

// 组件初始化
onMounted(async () => {
  await fetchServers()
})

// 在 script setup 中添加
const getContainerName = (containerId) => {
  const container = serverContainers.value.find(c => c.id === containerId)
  return container ? container.container_name : containerId
}
</script> 
