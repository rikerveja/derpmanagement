<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiHistory"
        title="ACL 配置历史"
        main
      >
        <div class="flex space-x-2">
          <BaseButton
            :icon="mdiRefresh"
            :loading="loading"
            @click="fetchLogs"
            label="刷新"
            color="info"
          />
          <BaseButton
            :icon="mdiDownload"
            label="导出"
            color="success"
            @click="exportLogs"
            :disabled="!logs.length"
          />
        </div>
      </SectionTitleLineWithButton>

      <CardBox>
        <div v-if="loading" class="flex justify-center items-center p-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <span class="ml-2">加载中...</span>
        </div>
        <div v-else>
          <div v-if="logs.length === 0" class="text-center py-8 text-gray-500">
            暂无日志数据
          </div>
          <div v-else>
            <textarea
              class="w-full h-96 p-4 font-mono text-sm bg-gray-50 border rounded"
              readonly
              v-model="formattedLogs"
            />
            <div class="mt-2 text-sm text-gray-500 flex justify-between items-center">
              <span>共 {{ logs.length }} 条记录</span>
              <span>最后更新: {{ new Date().toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiHistory, mdiRefresh, mdiDownload } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import api from '@/services/api'

const logs = ref([])
const loading = ref(false)

// 格式化日志显示
const formattedLogs = computed(() => {
  if (!logs.value.length) return ''
  
  return logs.value.map((log, index) => {
    const date = new Date(log.created_at)
    const formattedDate = date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    
    return `[${formattedDate}] User:${log.user_id} - ${log.details} (IP: ${log.ip_address})`
  }).join('\n')
})

// 获取日志
const fetchLogs = async () => {
  try {
    loading.value = true
    const response = await api.getAclLogs()
    console.log('API response:', response)
    
    if (response?.success && Array.isArray(response.logs)) {
      // 确保日志按时间倒序排序
      logs.value = [...response.logs].sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at)
      })
    } else {
      logs.value = []
    }
  } catch (error) {
    console.error('获取日志失败:', error)
    logs.value = []
  } finally {
    loading.value = false
  }
}

// 导出日志
const exportLogs = () => {
  if (!formattedLogs.value) {
    alert('没有可导出的日志数据')
    return
  }
  
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `acl-logs-${timestamp}.txt`
  const blob = new Blob([formattedLogs.value], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
textarea {
  resize: none;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

textarea:focus {
  outline: none;
}

/* 美化滚动条 */
textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style> 