<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiBell, 
  mdiRefresh, 
  mdiDelete, 
  mdiFilter,
  mdiAlertCircle,
  mdiServerNetwork,
  mdiDocker,
  mdiChartLine
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

const alerts = ref([])
const loading = ref(false)
const selectedType = ref('all')

// 告警类型映射
const alertTypeMap = {
  'General': '常规告警',
  'Monthly Traffic Limit Exceeded': '流量超限',
  'Server Health Issue': '服务器异常',
  'Docker Traffic Issue': 'Docker流量异常',
  'Docker Container Issue': 'Docker容器异常'
}

// 告警类型图标映射
const alertIconMap = {
  'General': mdiAlertCircle,
  'Monthly Traffic Limit Exceeded': mdiChartLine,
  'Server Health Issue': mdiServerNetwork,
  'Docker Traffic Issue': mdiDocker,
  'Docker Container Issue': mdiDocker
}

// 过滤后的告警列表
const filteredAlerts = computed(() => {
  if (selectedType.value === 'all') return alerts.value
  return alerts.value.filter(alert => alert.alert_type === selectedType.value)
})

// 获取告警列表
const fetchAlerts = async () => {
  try {
    loading.value = true
    const response = await api.getAlerts()
    if (response.success) {
      alerts.value = response.alerts.map(alert => ({
        ...alert,
        timestamp: new Date(alert.timestamp).toLocaleString()
      }))
    }
  } catch (error) {
    console.error('获取告警失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除告警
const deleteAlert = async (alertId) => {
  try {
    const response = await api.deleteAlert(alertId)
    if (response.success) {
      alerts.value = alerts.value.filter(alert => alert.id !== alertId)
    }
  } catch (error) {
    console.error('删除告警失败:', error)
  }
}

onMounted(() => {
  fetchAlerts()
  // 每30秒刷新一次数据
  const timer = setInterval(fetchAlerts, 30000)
  onUnmounted(() => clearInterval(timer))
})
</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiBell" title="告警管理" main>
      <BaseButton
        :icon="mdiRefresh"
        :loading="loading"
        @click="fetchAlerts"
        title="刷新"
      />
    </SectionTitleLineWithButton>

    <!-- 告警类型筛选 -->
    <CardBox class="mb-6">
      <div class="flex items-center space-x-4">
        <BaseButton
          :class="{ 'bg-blue-500 text-white': selectedType === 'all' }"
          @click="selectedType = 'all'"
        >
          全部
        </BaseButton>
        <BaseButton
          v-for="(name, type) in alertTypeMap"
          :key="type"
          :class="{ 'bg-blue-500 text-white': selectedType === type }"
          @click="selectedType = type"
        >
          {{ name }}
        </BaseButton>
      </div>
    </CardBox>

    <CardBox>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr>
              <th class="px-4 py-3 text-left">类型</th>
              <th class="px-4 py-3 text-left">消息</th>
              <th class="px-4 py-3 text-left">时间</th>
              <th class="px-4 py-3 text-left">状态</th>
              <th class="px-4 py-3 text-left">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in filteredAlerts" :key="alert.id"
                class="border-b border-gray-100 dark:border-gray-700">
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <BaseIcon
                    :path="alertIconMap[alert.alert_type]"
                    class="mr-2"
                    :class="{
                      'text-red-500': alert.status === 'active',
                      'text-gray-500': alert.status === 'resolved'
                    }"
                  />
                  {{ alertTypeMap[alert.alert_type] || alert.alert_type }}
                </div>
              </td>
              <td class="px-4 py-3">{{ alert.message }}</td>
              <td class="px-4 py-3">{{ alert.timestamp }}</td>
              <td class="px-4 py-3">
                <span :class="{
                  'px-2 py-1 rounded-full text-xs': true,
                  'bg-red-100 text-red-800': alert.status === 'active',
                  'bg-green-100 text-green-800': alert.status === 'resolved'
                }">
                  {{ alert.status === 'active' ? '活动' : '已解决' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <BaseButton
                  :icon="mdiDelete"
                  color="danger"
                  small
                  @click="deleteAlert(alert.id)"
                  title="删除告警"
                />
              </td>
            </tr>
            <tr v-if="filteredAlerts.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-500">
                暂无告警信息
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </CardBox>
  </SectionMain>
</template> 