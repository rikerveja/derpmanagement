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
  mdiChartLine,
  mdiCheck,
  mdiCheckCircle,
  mdiInformation
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'
import { message, Modal, Form, Input, Select, DatePicker, Button, Row, Col, Statistic, Space, Table, Tag, Descriptions } from 'ant-design-vue'
import dayjs from 'dayjs'

const alerts = ref([])
const loading = ref(false)
const selectedType = ref('all')
const detailsVisible = ref(false)
const resolveVisible = ref(false)
const resolving = ref(false)
const selectedAlert = ref(null)
const alertSettings = ref(null)
const checkInterval = ref(null)
const pollingTimer = ref(null)

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

// 筛选条件
const filters = ref({
  severity: '',
  status: '',
  dateRange: [],
})

// 解决表单
const resolveForm = ref({
  resolution_note: '',
})

// 表格列定义
const columns = [
  {
    title: '告警ID',
    dataIndex: 'id',
    key: 'id',
  },
  {
    title: '告警类型',
    dataIndex: 'alert_type',
    key: 'alert_type',
  },
  {
    title: '消息',
    dataIndex: 'message',
    key: 'message',
  },
  {
    title: '优先级',
    dataIndex: 'severity',
    key: 'severity',
    slots: { customRender: 'severity' },
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' },
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    render: (text) => formatDate(text),
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' },
  },
]

// 过滤后的告警列表
const filteredAlerts = computed(() => {
  let result = [...alerts.value]

  if (filters.value.severity) {
    result = result.filter(alert => alert.severity === filters.value.severity)
  }

  if (filters.value.status) {
    result = result.filter(alert => alert.status === filters.value.status)
  }

  if (filters.value.dateRange?.length === 2) {
    const startDate = filters.value.dateRange[0]
    const endDate = filters.value.dateRange[1]
    result = result.filter(alert => {
      const alertDate = dayjs(alert.created_at)
      return alertDate.isAfter(startDate) && alertDate.isBefore(endDate)
    })
  }

  return result
})

const totalAlerts = computed(() => alerts.value.length)
const activeAlerts = computed(() => alerts.value.filter(a => a.status === 'active').length)
const acknowledgedAlerts = computed(() => alerts.value.filter(a => a.status === 'acknowledged').length)
const resolvedAlerts = computed(() => alerts.value.filter(a => a.status === 'resolved').length)

// 获取告警列表
const fetchAlerts = async () => {
  try {
    loading.value = true
    const response = await api.alertApi.getAlerts()
    console.log('获取到的告警数据:', response) // 添加调试日志
    
    if (Array.isArray(response)) {
      alerts.value = response.map(alert => ({
        ...alert,
        timestamp: new Date(alert.created_at || alert.timestamp).toLocaleString(),
        status: alert.status || 'active',
        severity: alert.severity || 'medium'
      }))
    } else {
      console.warn('获取到的告警数据格式不正确:', response)
      alerts.value = []
    }
  } catch (error) {
    console.error('获取告警失败:', error)
    message.error('获取告警失败: ' + (error.response?.data?.message || error.message))
    alerts.value = []
  } finally {
    loading.value = false
  }
}

// 删除告警
const deleteAlert = async (alertId) => {
  try {
    await api.alertApi.deleteAlert(alertId)
    alerts.value = alerts.value.filter(alert => alert.id !== alertId)
    message.success('删除成功')
  } catch (error) {
    console.error('删除告警失败:', error)
    message.error('删除告警失败')
  }
}

const loadAlertSettings = async () => {
  try {
    const response = await api.alertApi.getAlertSettings()
    console.log('获取到的告警设置:', response) // 添加调试日志
    
    if (response) {
      alertSettings.value = response
      checkInterval.value = (response.checkInterval || 3) * 60 * 1000 // 默认3分钟
      startAlertChecks()
    } else {
      console.warn('获取到的告警设置为空')
      alertSettings.value = { checkInterval: 3 * 60 * 1000 } // 设置默认值
    }
  } catch (error) {
    console.error('加载告警设置失败:', error)
    message.error('加载告警设置失败: ' + (error.response?.data?.message || error.message))
    alertSettings.value = { checkInterval: 3 * 60 * 1000 } // 设置默认值
  }
}

const startAlertChecks = () => {
  stopAlertChecks()
  
  performAlertChecks()
  
  if (checkInterval.value) {
    pollingTimer.value = setInterval(() => {
      performAlertChecks()
    }, checkInterval.value)
  }
}

const stopAlertChecks = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

const parseNodeExporterMetrics = (metricsText) => {
  const metrics = {
    cpu_usage: 0,
    memory_usage: 0,
    disk_usage: 0,
    network_rx: 0,
    network_tx: 0
  }

  const lines = metricsText.split('\n')
  for (const line of lines) {
    if (line.startsWith('#') || !line) continue

    try {
      const [name, value] = line.split(' ')

      if (name.includes('node_cpu_seconds_total')) {
        metrics.cpu_usage = parseFloat(value)
      }
      else if (name.includes('node_memory_MemTotal_bytes')) {
        metrics.memory_usage = parseFloat(value)
      }
      else if (name.includes('node_filesystem_size_bytes')) {
        metrics.disk_usage = parseFloat(value)
      }
      else if (name.includes('node_network_receive_bytes_total')) {
        metrics.network_rx = parseFloat(value)
      }
      else if (name.includes('node_network_transmit_bytes_total')) {
        metrics.network_tx = parseFloat(value)
      }
    } catch (error) {
      console.warn('解析指标失败:', line, error)
    }
  }

  return metrics
}

const checkMetrics = async (container, metricsText) => {
  try {
    const metrics = parseNodeExporterMetrics(metricsText)
    
    if (metrics.cpu_usage > 80) {
      await api.alertApi.createAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} CPU使用率过高: ${metrics.cpu_usage.toFixed(2)}%`,
        severity: 'high',
        status: 'pending',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
    
    if (metrics.memory_usage > 85) {
      await api.alertApi.createAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} 内存使用率过高: ${metrics.memory_usage.toFixed(2)}%`,
        severity: 'high',
        status: 'pending',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
    
    if (metrics.disk_usage > 90) {
      await api.alertApi.createAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} 磁盘使用率过高: ${metrics.disk_usage.toFixed(2)}%`,
        severity: 'critical',
        status: 'pending',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
  } catch (error) {
    console.error(`解析容器 ${container.name || container.id} 指标失败:`, error)
  }
}

const performAlertChecks = async () => {
  if (!alertSettings.value) return

  try {
    loading.value = true
    
    const containersResponse = await api.containerApi.getContainers()
    console.log('获取到的容器数据:', containersResponse) // 添加调试日志
    
    if (!containersResponse || (!Array.isArray(containersResponse) && !containersResponse.containers)) {
      console.warn('获取到的容器数据格式不正确:', containersResponse)
      return
    }

    const containers = Array.isArray(containersResponse) 
      ? containersResponse 
      : containersResponse.containers || []
    
    for (const container of containers) {
      try {
        if (!container.ip || !container.port) {
          console.warn(`容器缺少必要属性:`, container)
          continue
        }

        const healthCheckUrl = `http://${container.ip}:${container.port}`
        console.log(`检查容器健康状态: ${healthCheckUrl}`) // 添加调试日志
        
        const healthResponse = await fetch(healthCheckUrl, { 
          timeout: 5000,
          mode: 'no-cors' // 添加这个选项以处理跨域问题
        })
        
        if (!healthResponse.ok) {
          await api.alertApi.createAlert({
            alert_type: 'Docker Container Issue',
            message: `容器 ${container.name || container.id} (${container.ip}:${container.port}) 不可访问`,
            severity: 'critical',
            status: 'active',
            source: container.name || container.id,
            timestamp: new Date().toISOString()
          })
        }

        if (container.node_exporter_port) {
          const metricsUrl = `http://${container.ip}:${container.node_exporter_port}/metrics`
          console.log(`获取容器指标: ${metricsUrl}`) // 添加调试日志
          
          const metricsResponse = await fetch(metricsUrl, {
            mode: 'no-cors' // 添加这个选项以处理跨域问题
          })
          if (metricsResponse.ok) {
            const metricsText = await metricsResponse.text()
            await checkMetrics(container, metricsText)
          }
        }
      } catch (error) {
        console.error(`检查容器 ${container.name || container.id} 失败:`, error)
        await api.alertApi.createAlert({
          alert_type: 'Docker Container Issue',
          message: `容器 ${container.name || container.id} 检查失败: ${error.message}`,
          severity: 'high',
          status: 'active',
          source: container.name || container.id,
          timestamp: new Date().toISOString()
        })
      }
    }

    await fetchAlerts()
  } catch (error) {
    console.error('执行告警检查失败:', error)
    message.error('执行告警检查失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const refreshAlerts = async () => {
  try {
    loading.value = true
    await fetchAlerts()
  } catch (error) {
    console.error('刷新告警列表失败:', error)
    message.error('刷新告警列表失败')
  } finally {
    loading.value = false
  }
}

const handleAcknowledge = async (alert) => {
  try {
    await api.alertApi.updateAlertStatus(alert.id, 'acknowledged')
    message.success('告警已确认')
    await refreshAlerts()
  } catch (error) {
    console.error('确认告警失败:', error)
    message.error('确认告警失败')
  }
}

const handleResolve = (alert) => {
  selectedAlert.value = alert
  resolveVisible.value = true
}

const confirmResolve = async () => {
  if (!selectedAlert.value) return
  
  resolving.value = true
  try {
    await api.alertApi.updateAlertStatus(
      selectedAlert.value.id, 
      'resolved',
      resolveForm.value.resolution_note
    )
    message.success('告警已解决')
    resolveVisible.value = false
    resolveForm.value.resolution_note = ''
    await refreshAlerts()
  } catch (error) {
    console.error('解决告警失败:', error)
    message.error('解决告警失败')
  } finally {
    resolving.value = false
  }
}

const showDetails = (record) => {
  selectedAlert.value = record
  detailsVisible.value = true
}

const handleFilterChange = () => {
  refreshAlerts()
}

// 工具方法
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getSeverityColor = (severity) => {
  const colors = {
    critical: '#cf1322',
    high: '#fa541c',
    medium: '#faad14',
    low: '#52c41a'
  }
  return colors[severity] || '#d9d9d9'
}

const getSeverityText = (severity) => {
  const texts = {
    critical: '严重',
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[severity] || severity
}

const getStatusColor = (status) => {
  const colors = {
    active: '#cf1322',
    acknowledged: '#faad14',
    resolved: '#52c41a'
  }
  return colors[status] || '#d9d9d9'
}

const getStatusText = (status) => {
  const texts = {
    active: '活跃',
    acknowledged: '已确认',
    resolved: '已解决'
  }
  return texts[status] || status
}

onMounted(async () => {
  await loadAlertSettings()
})

onUnmounted(() => {
  stopAlertChecks()
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

    <!-- 告警统计 -->
    <div class="alert-statistics">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-statistic title="总告警数" :value="totalAlerts" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="活跃告警" :value="activeAlerts" :valueStyle="{ color: '#cf1322' }" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="已确认" :value="acknowledgedAlerts" :valueStyle="{ color: '#faad14' }" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="已解决" :value="resolvedAlerts" :valueStyle="{ color: '#3f8600' }" />
        </a-col>
      </a-row>
    </div>

    <!-- 筛选器 -->
    <div class="alert-filters">
      <a-space>
        <a-select
          v-model:value="filters.severity"
          placeholder="优先级"
          style="width: 120px"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="critical">严重</a-select-option>
          <a-select-option value="high">高</a-select-option>
          <a-select-option value="medium">中</a-select-option>
          <a-select-option value="low">低</a-select-option>
        </a-select>

        <a-select
          v-model:value="filters.status"
          placeholder="状态"
          style="width: 120px"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="active">活跃</a-select-option>
          <a-select-option value="acknowledged">已确认</a-select-option>
          <a-select-option value="resolved">已解决</a-select-option>
        </a-select>

        <a-range-picker
          v-model:value="filters.dateRange"
          @change="handleFilterChange"
        />

        <a-button type="primary" @click="refreshAlerts">
          刷新
        </a-button>
      </a-space>
    </div>

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
                      'text-yellow-500': alert.status === 'acknowledged',
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
                  'bg-yellow-100 text-yellow-800': alert.status === 'acknowledged',
                  'bg-green-100 text-green-800': alert.status === 'resolved'
                }">
                  {{ getStatusText(alert.status) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <a-space>
                  <!-- 确认按钮 -->
                  <BaseButton
                    v-if="alert.status === 'active'"
                    :icon="mdiCheck"
                    color="warning"
                    small
                    @click="handleAcknowledge(alert)"
                    title="确认告警"
                  />
                  <!-- 解决按钮 -->
                  <BaseButton
                    v-if="['active', 'acknowledged'].includes(alert.status)"
                    :icon="mdiCheckCircle"
                    color="success"
                    small
                    @click="handleResolve(alert)"
                    title="解决告警"
                  />
                  <!-- 删除按钮 -->
                  <BaseButton
                    :icon="mdiDelete"
                    color="danger"
                    small
                    @click="deleteAlert(alert.id)"
                    title="删除告警"
                  />
                  <!-- 详情按钮 -->
                  <BaseButton
                    :icon="mdiInformation"
                    color="info"
                    small
                    @click="showDetails(alert)"
                    title="查看详情"
                  />
                </a-space>
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

    <!-- 告警详情弹窗 -->
    <a-modal
      v-model:visible="detailsVisible"
      title="告警详情"
      width="700px"
      :footer="null"
    >
      <template v-if="selectedAlert">
        <a-descriptions bordered>
          <a-descriptions-item label="告警ID" span="3">
            {{ selectedAlert.id }}
          </a-descriptions-item>
          <a-descriptions-item label="告警类型" span="3">
            {{ selectedAlert.alert_type }}
          </a-descriptions-item>
          <a-descriptions-item label="告警消息" span="3">
            {{ selectedAlert.message }}
          </a-descriptions-item>
          <a-descriptions-item label="优先级">
            <a-tag :color="getSeverityColor(selectedAlert.severity)">
              {{ getSeverityText(selectedAlert.severity) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(selectedAlert.status)">
              {{ getStatusText(selectedAlert.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ formatDate(selectedAlert.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="解决时间" span="3" v-if="selectedAlert.resolved_at">
            {{ formatDate(selectedAlert.resolved_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="解决说明" span="3" v-if="selectedAlert.details?.resolution_note">
            {{ selectedAlert.details.resolution_note }}
          </a-descriptions-item>
        </a-descriptions>
      </template>
    </a-modal>

    <!-- 解决告警弹窗 -->
    <a-modal
      v-model:visible="resolveVisible"
      title="解决告警"
      @ok="confirmResolve"
      :confirmLoading="resolving"
    >
      <a-form :model="resolveForm" layout="vertical">
        <a-form-item label="解决说明" name="resolution_note">
          <a-textarea
            v-model:value="resolveForm.resolution_note"
            :rows="4"
            placeholder="请输入解决说明"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </SectionMain>
</template>

<style scoped>
.alert-list-container {
  padding: 24px;
}

.alert-statistics {
  margin-bottom: 24px;
  background: #fafafa;
  padding: 24px;
  border-radius: 2px;
}

.alert-filters {
  margin-bottom: 24px;
}
</style> 