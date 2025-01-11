import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useServerStore = defineStore('servers', () => {
  const servers = ref({})
  
  async function fetchServerDetails(serverId) {
    if (servers.value[serverId]) {
      return servers.value[serverId]
    }
    
    try {
      const response = await api.getServer(serverId)
      if (response.success) {
        servers.value[serverId] = response.server
        return response.server
      }
    } catch (error) {
      console.error('获取服务器详情失败:', error)
    }
    return null
  }
  
  return {
    servers,
    fetchServerDetails
  }
}) 