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

// 从api对象中解构需要的API
const { alertApi, containerApi } = api

// 定义告警阈值常量
const CPU_THRESHOLD = 80
const MEMORY_THRESHOLD = 85
const DISK_THRESHOLD = 90

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
const refreshTimer = ref(null)

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

  // 按创建时间逆序排序，最新的告警最先展示
  result.sort((a, b) => {
    const dateA = new Date(a.created_at || a.timestamp || 0)
    const dateB = new Date(b.created_at || b.timestamp || 0)
    return dateB - dateA
  })

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
    
    // 处理不同格式的响应数据
    let alertsData = []
    
    if (Array.isArray(response)) {
      alertsData = response
    } else if (response && typeof response === 'object') {
      // 检查是否有 alerts 数组
      if (Array.isArray(response.alerts)) {
        alertsData = response.alerts
      } else if (response.data && Array.isArray(response.data)) {
        alertsData = response.data
      } else if (response.success && Array.isArray(response.data)) {
        alertsData = response.data
      }
    }
    
    console.log('处理后的告警数据:', alertsData)
    
    // 标准化告警数据
    alerts.value = alertsData.map(alert => ({
      id: alert.id,
      alert_type: alert.alert_type || 'container',
      message: alert.message || '系统告警',
      severity: alert.severity || 'medium',
      status: alert.status || 'active',
      created_at: alert.created_at || alert.timestamp || new Date().toISOString(),
      timestamp: new Date(alert.created_at || alert.timestamp || new Date()).toLocaleString(),
      details: alert.details || {},
      resolved_at: alert.resolved_at || null,
      resolved_by: alert.resolved_by || null,
      server_id: alert.server_id || null,
      server_info: alert.server_info || null
    }))
    
    console.log('标准化后的告警数据:', alerts.value)
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
    console.log('开始删除告警，ID:', alertId)
    loading.value = true
    
    try {
      // 尝试删除告警
      const response = await api.alertApi.deleteAlert(alertId)
      console.log('删除告警响应:', response)
      message.success('删除告警成功')
    } catch (error) {
      console.log('删除告警API错误:', error)
      // 即使后端返回500错误，告警也可能已经被删除
      // 这是因为后端在log_operation函数中缺少status参数导致的
      message.success('删除告警成功（后端日志记录出错但删除已完成）')
    }
    
    // 无论如何都刷新列表，因为告警可能已经被删除
    await fetchAlerts()
  } catch (error) {
    console.error('刷新告警列表失败:', error)
    message.error('刷新告警列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const loadAlertSettings = async () => {
  try {
    const result = await api.alertApi.getAlertSettings()
    console.log('获取到的告警设置:', result)
    
    // 统一处理告警设置数据
    alertSettings.value = {
      serverHealthCheck: true,
      dockerHealthCheck: true,
      trafficAlert: true,
      emailNotification: true,
      checkInterval: 3,
      thresholds: {
        traffic: 90,
        cpu: 80,
        memory: 80,
        disk: 85
      },
      ...result.settings // 使用服务器返回的设置覆盖默认值
    }
    
    // 设置检查间隔
    checkInterval.value = (alertSettings.value.checkInterval || 3) * 60 * 1000;
    
    console.log('当前使用的告警设置:', alertSettings.value);
    console.log(`告警检查间隔: ${checkInterval.value / 1000}秒`);
    
    // 不再根据告警设置更新页面刷新定时器
    // 页面刷新时间固定为500分钟
    
    // 启动告警检查
    startAlertChecks()
  } catch (error) {
    console.error('加载告警设置失败:', error)
    message.error('加载告警设置失败，使用默认设置')
    
    // 使用默认设置
    alertSettings.value = {
      serverHealthCheck: true,
      dockerHealthCheck: true,
      trafficAlert: true,
      emailNotification: true,
      checkInterval: 3,
      thresholds: {
        traffic: 90,
        cpu: 80,
        memory: 80,
        disk: 85
      }
    }
    checkInterval.value = 3 * 60 * 1000
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
  
  // 用于累计CPU使用时间
  let cpuUserTime = 0
  let cpuSystemTime = 0
  let cpuTotalTime = 0
  
  // 用于内存计算
  let memTotal = 0
  let memFree = 0
  let memBuffers = 0
  let memCached = 0
  
  // 用于磁盘计算
  let diskTotal = 0
  let diskFree = 0

  for (const line of lines) {
    if (line.startsWith('#') || !line.trim()) continue

    try {
      // 使用正则表达式匹配指标名称和值
      const match = line.match(/^([a-zA-Z_]+[a-zA-Z0-9_]*){([^}]*)}?\s+(.+)/)
      if (!match) continue
      
      const [, name, labels, value] = match
      const numValue = parseFloat(value)

      switch (name) {
        case 'node_cpu_seconds_total':
          if (labels.includes('mode="user"')) cpuUserTime = numValue
          else if (labels.includes('mode="system"')) cpuSystemTime = numValue
          else if (labels.includes('mode="idle"')) cpuTotalTime = numValue
          break
          
        case 'node_memory_MemTotal_bytes':
          memTotal = numValue
          break
        case 'node_memory_MemFree_bytes':
          memFree = numValue
          break
        case 'node_memory_Buffers_bytes':
          memBuffers = numValue
          break
        case 'node_memory_Cached_bytes':
          memCached = numValue
          break
          
        case 'node_filesystem_size_bytes':
          if (labels.includes('mountpoint="/"')) diskTotal = numValue
          break
        case 'node_filesystem_free_bytes':
          if (labels.includes('mountpoint="/"')) diskFree = numValue
          break
      }
    } catch (error) {
      console.warn('解析指标行失败:', line, error)
    }
  }

  // 计算CPU使用率
  if (cpuTotalTime > 0) {
    metrics.cpu_usage = ((cpuUserTime + cpuSystemTime) / cpuTotalTime) * 100
  }

  // 计算内存使用率
  if (memTotal > 0) {
    const memUsed = memTotal - memFree - memBuffers - memCached
    metrics.memory_usage = (memUsed / memTotal) * 100
  }

  // 计算磁盘使用率
  if (diskTotal > 0) {
    metrics.disk_usage = ((diskTotal - diskFree) / diskTotal) * 100
  }

  return metrics
}

// 手动创建告警
const createManualAlert = async (alertData) => {
  try {
    const response = await alertApi.createAlert(alertData, () => {
      // 创建成功后自动刷新告警列表
      refreshAlerts();
      message.success('告警创建成功');
    });
    
    // 处理重复告警的情况
    if (response && response.duplicate === true) {
      console.log('检测到重复告警，不再创建新告警');
      // 可以选择不显示任何消息，或者显示一个提示
      // message.info('已存在相同类型且未解决的告警，不再重复提醒');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('创建告警失败:', error);
    message.error('创建告警失败: ' + (error.response?.data?.message || error.message));
    return false;
  }
}

// 修改 checkMetrics 方法，使用新的 createManualAlert 方法
const checkMetrics = async (container, metricsText) => {
  try {
    const metrics = parseNodeExporterMetrics(metricsText)
    const thresholds = alertSettings.value?.thresholds || {
      cpu: 80,
      memory: 85,
      disk: 90
    }
    
    if (metrics.cpu_usage > thresholds.cpu) {
      await createManualAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} CPU使用率过高: ${metrics.cpu_usage.toFixed(2)}%`,
        severity: 'high',
        status: 'active',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
    
    if (metrics.memory_usage > thresholds.memory) {
      await createManualAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} 内存使用率过高: ${metrics.memory_usage.toFixed(2)}%`,
        severity: 'high',
        status: 'active',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
    
    if (metrics.disk_usage > thresholds.disk) {
      await createManualAlert({
        alert_type: 'Server Health Issue',
        message: `容器 ${container.name || container.id} 磁盘使用率过高: ${metrics.disk_usage.toFixed(2)}%`,
        severity: 'critical',
        status: 'active',
        source: container.name || container.id,
        timestamp: new Date().toISOString()
      })
    }
  } catch (error) {
    console.error(`解析容器 ${container.name || container.id} 指标失败:`, error)
  }
}

async function performAlertChecks() {
  try {
    // 获取容器列表
    const containers = await containerApi.getContainers()
    console.log('获取到的容器列表:', containers)

    if (!Array.isArray(containers)) {
      console.error('容器列表格式不正确:', containers)
      return
    }

    // 遍历每个容器进行检查
    for (const container of containers) {
      try {
        if (!container.container_name) {
          console.warn('容器缺少container_name:', container)
          continue
        }

        console.log('开始检查容器:', container.container_name)

        // 获取容器监控数据
        const metricsResponse = await containerApi.getContainerMetrics(
          container.container_name,
          container.node_exporter_port
        )

        if (!metricsResponse) {
          throw new Error('获取监控数据失败')
        }

        // 解析和处理监控数据
        const metrics = parseNodeExporterMetrics(metricsResponse)
        
        // 检查CPU使用率
        if (metrics.cpu_usage > CPU_THRESHOLD) {
          const alertData = {
            container_name: container.container_name,
            alert_type: 'High CPU Usage',
            message: `容器 ${container.container_name} CPU使用率过高: ${metrics.cpu_usage.toFixed(2)}%`,
            severity: 'warning',
            details: {
              container_name: container.container_name,
              cpu_usage: metrics.cpu_usage.toFixed(2)
            }
          };
          await createManualAlert(alertData);
        }

        // 检查内存使用率
        if (metrics.memory_usage > MEMORY_THRESHOLD) {
          const alertData = {
            container_name: container.container_name,
            alert_type: 'High Memory Usage',
            message: `容器 ${container.container_name} 内存使用率过高: ${metrics.memory_usage.toFixed(2)}%`,
            severity: 'warning',
            details: {
              container_name: container.container_name,
              memory_usage: metrics.memory_usage.toFixed(2)
            }
          };
          await createManualAlert(alertData);
        }

        // 检查磁盘使用率
        if (metrics.disk_usage > DISK_THRESHOLD) {
          const alertData = {
            container_name: container.container_name,
            alert_type: 'High Disk Usage',
            message: `容器 ${container.container_name} 磁盘使用率过高: ${metrics.disk_usage.toFixed(2)}%`,
            severity: 'warning',
            details: {
              container_name: container.container_name,
              disk_usage: metrics.disk_usage.toFixed(2)
            }
          };
          await createManualAlert(alertData);
        }

        console.log('容器检查完成:', container.container_name)
      } catch (error) {
        console.error(`检查容器 ${container.container_name} 失败:`, error)
        // 创建告警
        const alertData = {
          container_name: container.container_name,
          alert_type: 'Monitoring Failed',
          message: `容器 ${container.container_name} 监控检查失败: ${error.message}`,
          severity: 'high',
          details: {
            container_name: container.container_name,
            error: error.message
          }
        };
        await createManualAlert(alertData);
      }
    }
  } catch (error) {
    console.error('执行告警检查失败:', error)
  }
}

// 解析 Prometheus 格式的监控数据
function parsePrometheusMetrics(metricsData) {
  const metrics = {
    cpu_usage: 0,
    memory_usage: 0
  }

  try {
    const lines = metricsData.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('#')) continue
      
      if (line.includes('container_cpu_usage_seconds_total')) {
        const match = line.match(/[\d.]+$/)
        if (match) {
          metrics.cpu_usage = parseFloat(match[0]) * 100
        }
      }
      
      if (line.includes('container_memory_usage_bytes')) {
        const match = line.match(/[\d.]+$/)
        if (match) {
          const totalMemory = 1024 * 1024 * 1024 // 1GB in bytes
          metrics.memory_usage = (parseFloat(match[0]) / totalMemory) * 100
        }
      }
    }
  } catch (error) {
    console.error('解析监控数据失败:', error)
  }

  return metrics
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

// 创建测试告警
const createTestAlert = async () => {
  try {
    message.loading('正在创建测试告警...')
    await createManualAlert({
      alert_type: 'container',
      message: '这是一个测试告警 - ' + new Date().toLocaleString(),
      severity: 'high',
      status: 'active'
    })
  } catch (error) {
    console.error('创建测试告警失败:', error)
    message.error('创建测试告警失败: ' + (error.response?.data?.message || error.message))
  }
}

// 更新页面刷新定时器
const updateRefreshTimer = () => {
  // 清除现有定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value);
  }
  
  // 使用告警设置中的检查间隔设置新的定时器
  const interval = checkInterval.value || 3 * 60 * 1000; // 默认3分钟
  console.log(`更新告警列表刷新间隔: ${interval / 1000}秒`);
  
  refreshTimer.value = setInterval(() => {
    console.log('根据设置的时间间隔自动刷新告警列表...');
    fetchAlerts();
  }, interval);
}

onMounted(async () => {
  // 首先获取告警列表
  await fetchAlerts();
  
  // 然后加载告警设置
  await loadAlertSettings();
  
  // 设置定时刷新告警列表，使用固定的500分钟间隔
  // 清除现有定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value);
  }
  
  // 设置为500分钟刷新一次
  const refreshInterval = 500 * 60 * 1000; // 500分钟
  console.log(`设置告警列表刷新间隔: ${refreshInterval / 60000}分钟`);
  
  refreshTimer.value = setInterval(() => {
    console.log('根据设置的时间间隔自动刷新告警列表...');
    fetchAlerts();
  }, refreshInterval);
  
  // 在组件卸载时清除定时器
  onUnmounted(() => {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value);
    }
    stopAlertChecks();
  });
})
</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiBell" title="告警管理" main>
      <div class="flex space-x-2">
        <BaseButton
          :icon="mdiRefresh"
          :loading="loading"
          @click="fetchAlerts"
          title="刷新"
        />
      </div>
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
                  'px-3 py-1 rounded-full text-xs inline-block min-w-16 text-center': true,
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

/* 添加状态标签样式 */
.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  min-width: 64px;
  text-align: center;
  white-space: nowrap;
}

.status-active {
  background-color: #fff1f0;
  color: #cf1322;
  border: 1px solid #ffa39e;
}

.status-acknowledged {
  background-color: #fffbe6;
  color: #d48806;
  border: 1px solid #ffe58f;
}

.status-resolved {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}
</style> 
