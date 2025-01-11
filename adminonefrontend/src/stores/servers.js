import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useServerStore = defineStore('servers', () => {
  const servers = ref({})
  
  async function fetchServerDetails(serverId) {
    if (servers.value[serverId]) {
      return servers.value[serverId]
    }
    
    try {
      const response = await axios.get(`http://100.82.38.13:8000/api/server/status/${serverId}`)
      if (response.data.success) {
        servers.value[serverId] = response.data.server_info
        return response.data.server_info
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
