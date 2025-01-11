<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiHeartPulse,
  mdiRefresh,
} from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

// 服务器健康状态列表
const servers = ref([])
const loading = ref(false)
const loadingMessage = ref('正在检查服务器状态，这可能需要20-30秒...')

// 获取所有服务器的健康状态
const fetchServersHealth = async () => {
  try {
    loading.value = true
    loadingMessage.value = '正在检查服务器状态，这可能需要20-30秒...'
    console.log('开始请求健康检查...')
    const response = await api.getServerHealthCheck()
    console.log('健康检查响应:', response)
    if (response?.success && response?.health_check_results?.success) {
      loadingMessage.value = '正在获取服务器详细信息...'
      // 获取所有服务器的基本信息
      const serversResponse = await api.getServers()
      console.log('服务器列表响应:', serversResponse)
      const serversMap = {}
      if (serversResponse?.success) {
        serversResponse.servers.forEach(server => {
          console.log('映射服务器:', server.id, server)
          serversMap[server.id] = server
        })
      }
      
      // 合并健康检查结果和服务器信息
      const healthData = response.health_check_results.data
      console.log('健康检查数据:', healthData)
      console.log('服务器映射:', serversMap)
      servers.value = healthData.map(health => {
        const serverInfo = serversMap[health.server_id]
        console.log('处理服务器:', health.server_id, serverInfo)
        return {
          ...health,
          server_name: serverInfo?.server_name || `Server ${health.server_id}`,
          region: serverInfo?.region || '-',
          config: serverInfo ? 
            `${serverInfo.cpu}核 / ${serverInfo.memory}GB / ${serverInfo.storage}GB` : 
            '-',
          updated_at: serverInfo?.updated_at || '-'
        }
      })
      console.log('最终处理结果:', servers.value)
    } else {
      servers.value = []
      console.warn('获取服务器健康状态失败:', response)
    }
  } catch (error) {
    console.error('获取服务器健康状态失败:', error)
    servers.value = []
  } finally {
    loading.value = false
  }
}

// 获取状态样式
const getStatusStyle = (status) => {
  switch (status) {
    case 'reachable':
      return 'bg-green-100 text-green-800'
    case 'unreachable':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-yellow-100 text-yellow-800'
  }
}

onMounted(fetchServersHealth)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox class="mb-6">
        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold flex items-center">
            <BaseIcon :path="mdiHeartPulse" class="mr-2" />
            服务器健康状态
          </h1>
          <BaseButton
            :icon="mdiRefresh"
            color="info"
            :loading="loading"
            @click="fetchServersHealth"
            title="刷新状态"
          />
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-sm font-bold">服务器名称</th>
                <th class="px-4 py-3 text-left text-sm font-bold">IP地址</th>
                <th class="px-4 py-3 text-left text-sm font-bold">地区</th>
                <th class="px-4 py-3 text-left text-sm font-bold">配置</th>
                <th class="px-4 py-3 text-left text-sm font-bold">状态</th>
                <th class="px-4 py-3 text-left text-sm font-bold">错误信息</th>
                <th class="px-4 py-3 text-left text-sm font-bold">最后更新时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="server in servers" :key="server.server_id" 
                  class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  {{ server.server_name }}
                </td>
                <td class="px-4 py-3 font-mono text-sm">
                  {{ server.ip_address }}
                </td>
                <td class="px-4 py-3">
                  {{ server.region }}
                </td>
                <td class="px-4 py-3 text-sm">
                  {{ server.config }}
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                        :class="getStatusStyle(server.status.status)">
                    {{ server.status.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-red-600">
                  {{ server.status.error || '-' }}
                </td>
                <td class="px-4 py-3 text-sm">-</td>
              </tr>
              <tr v-if="loading">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  <div class="flex items-center justify-center">
                    <div class="flex flex-col items-center">
                      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
                      <span>{{ loadingMessage }}</span>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!loading && servers.length === 0">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  暂无服务器数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.table-row-loading {
  opacity: 0.5;
  pointer-events: none;
}
</style> 
