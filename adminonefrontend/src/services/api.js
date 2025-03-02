import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token和日志
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  console.log('Request Config:', {
    url: config.url,
    method: config.method,
    headers: config.headers,
    data: config.data,
    timestamp: new Date().toISOString(),
    isOptions: config.method.toLowerCase() === 'options'
  });
  return config
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  response => {
    // 登录接口特殊处理
    if (response.config.url === '/login') {
      return {
        success: true,
        token: response.data.token,
        data: response.data.user || response.data,
        message: response.data.message
      }
    }
    // 其他接口直接返回数据
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/adminonefrontend/login'
    }
    return Promise.reject(error)
  }
)

// 序列号相关 API
const getSerials = () => {
  return api.get('/serials')
}

const generateSerials = (data) => {
  return api.post('/serial/generate', {
    "count": data.count,
    "valid_days": parseInt(data.valid_days),
    "prefix": data.prefix
  })
}

const deleteSerial = (data) => {
  return api.delete('/serial/delete', {
    data: data // 这里直接使用传入的对象
  })
}

const batchDeleteSerials = (codes) => {
  return api.delete('/serial/delete', {
    data: {
      "serial_codes": codes
    }
  })
}

// 服务器相关 API
const getServers = () => {
  return api.get('/get_servers')
}

const getServerCategories = () => {
  return api.get('/server/categories')  // 获取服务器分类
}

const addServer = (serverData) => {
  console.log('准备发送的服务器数据:', serverData)
  const requestData = {
    ip_address: serverData.ip_address,
    region: serverData.region,
    cpu: serverData.cpu,
    memory: serverData.memory,
    category_id: serverData.category_id,
    server_name: serverData.server_name,
    storage: serverData.storage,
    bandwidth: serverData.bandwidth,
    user_count: serverData.user_count,
    total_traffic: serverData.total_traffic
  }
  console.log('转换后的请求数据:', requestData)
  console.log('请求URL:', '/add_server')
  return api.post('/add_server', requestData)
}

// 更新服务器
const updateServer = (serverId, serverData) => {
  console.log('准备更新服务器数据:', serverData)
  const requestData = {
    ip_address: serverData.ip_address,
    region: serverData.region,
    cpu: serverData.cpu,
    memory: serverData.memory,
    category_id: serverData.category_id,
    server_name: serverData.server_name,
    storage: serverData.storage,
    bandwidth: serverData.bandwidth,
    user_count: serverData.user_count,
    total_traffic: serverData.total_traffic
  }
  console.log('转换后的请求数据:', requestData)
  console.log('请求URL:', `/update_server/${serverId}`)
  return api.put(`/update_server/${serverId}`, requestData)
}

const deleteServer = (serverId) => {
  return api.delete(`/delete_server/${serverId}`)
}

const getServerHealthCheck = () => {
  return api.get('/server/health_check')
}

// ACL相关API
const generateAcl = (data) => {
  // 转换数据格式以匹配后端API要求
  const requestData = {
    user_id: data.user_id,
    container_ids: data.container_ids,
    server_id: data.server_id,  // 单个服务器ID
    is_active: data.is_active
  }
  console.log('发送生成ACL请求:', requestData)
  return api.post('/acl/generate', requestData)
}

const getAclLogs = (userId) => {
  return api.get(`/acl/logs/${userId}`)
}

const downloadAcl = (userId) => {
  return api.get(`/acl/download/${userId}`)
}

const getAclList = () => {
  return api.get('/acl/list')
}

const getUser = (userId) => {
  return api.get(`/user/${userId}`)
}

const getServer = (serverId) => {
  return api.get(`/server/${serverId}`)
}

const getContainer = (containerId) => {
  return api.get(`/container/${containerId}`)
}

// ACL配置相关
const getAclConfigs = () => {
  return api.get('/acl/configs')
}

// 获取服务器的容器列表
const getServerContainers = (serverId) => {
  return api.get('/containers', {
    params: {
      server_id: serverId
    }
  })
}

// 仪表盘相关 API
const dashboardApi = {
  // 获取系统概览
  getSystemOverview() {
    return api.get('/system/overview')
  },

  // 获取所有用户
  getAllUsers() {
    return api.get('/users').then(response => {
      if (response.data) {
        return {
          success: true,
          users: response.data.users || []
        }
      }
      throw new Error('Invalid response format')
    }).catch(error => {
      console.error('Get users error:', error)
      return {
        success: false,
        message: error.message,
        users: []
      }
    })
  },

  // 获取所有服务器
  getServers() {
    return api.get('/get_servers')
  },

  // 获取所有容器
  getContainers() {
    return api.get('/containers')
  },

  // 获取实时流量
  getRealTimeTraffic() {
    return api.get('/traffic/realtime')
  },

  // 获取告警信息
  getAlerts() {
    return api.get('/alerts/all')
      .then(response => response.data)
  },

  // 获取租赁信息
  getRentals() {
    return api.get('/rentals/all')
      .then(response => {
        console.log('API getRentals response:', response)
        if (response.data) {
          // 确保每个租赁对象都包含用户信息
          const rentals = response.data.rentals || response.data
          return {
            success: true,
            rentals: rentals.map(rental => ({
              ...rental,
              // 确保用户信息存在
              user_info: rental.user_info || {
                email: rental.user_email || rental.email,
                username: rental.username
              }
            })),
            message: response.data.message || '获取成功'
          }
        }
        return response
      })
      .catch(error => {
        console.error('API getRentals error:', error)
        throw error
      })
  },

  // 获取收入统计
  getIncomeStats() {
    return api.get('/income/stats')
  }
}

// 流量相关 API
const trafficApi = {
  // 获取所有容器的实时流量
  getAllContainersTraffic() {
    return api.get('/traffic/realtime')
  },

  // 获取单个容器的实时流量
  getContainerTraffic(containerId) {
    return api.get(`/traffic/realtime/${containerId}`)
  },

  // 获取用户流量历史
  getTrafficHistory(userId) {
    return api.get(`/traffic/history/${userId}`)
  },

  // 获取流量统计
  getTrafficStats(params) {
    return api.post('/traffic/stats', params)
  }
}

/**
 * 保存容器流量数据
 * @param {Object} data - 流量数据对象
 * @param {string} data.container_id - 容器ID（原始ID，不是自增ID）
 * @param {number} data.upload_traffic - 上传流量（字节）
 * @param {number} data.download_traffic - 下载流量（字节）
 * @param {number} data.remaining_traffic - 剩余流量（字节）
 * @returns {Promise} 返回保存结果
 */
const saveTrafficData = async (data) => {
  try {
    // 确保所有数值都是整数（字节）
    const requestData = {
      container_id: data.container_id,
      upload_traffic: Math.floor(data.upload_traffic || 0),
      download_traffic: Math.floor(data.download_traffic || 0),
      remaining_traffic: Math.floor(data.remaining_traffic || 0)
    }

    console.log('发送流量数据:', requestData)
    const response = await api.post('/traffic/save_traffic', requestData)
    
    if (response.message === 'Traffic data saved successfully') {
      return response
    } else {
      throw new Error(response.error || '保存失败')
    }
  } catch (error) {
    console.error('保存流量数据失败:', error)
    throw new Error(error.response?.error || '保存流量数据失败')
  }
}

export const alarmRuleApi = {
  // 获取告警规则列表
  getRules: async (category = '') => {
    const url = category ? `/alerts/rules?category=${category}` : '/alerts/rules';
    return await api.get(url);
  },

  // 创建新的告警规则
  createRule: async (ruleData) => {
    return await api.post('/alerts/rules', ruleData);
  },

  // 更新告警规则
  updateRule: async (ruleId, ruleData) => {
    return await api.put(`/alerts/rules/${ruleId}`, ruleData);
  },

  // 删除告警规则
  deleteRule: async (ruleId) => {
    return await api.delete(`/alerts/rules/${ruleId}`);
  }
};

// 修改原有的告警相关 API
const alertApi = {
  // 获取告警列表
  getAlerts: () => {
    console.log('开始获取告警列表...')
    return api.get('/alerts')
      .then(response => {
        console.log('原始告警响应:', response)
        
        // 尝试从不同的响应结构中获取告警数据
        let alerts = []
        
        if (Array.isArray(response)) {
          alerts = response
        } else if (response && typeof response === 'object') {
          if (Array.isArray(response.alerts)) {
            alerts = response.alerts
          } else if (response.data && Array.isArray(response.data)) {
            alerts = response.data
          } else if (response.success && Array.isArray(response.data)) {
            alerts = response.data
          }
        }
        
        console.log('处理后的告警数据:', alerts)
        return alerts
      })
      .catch(error => {
        console.error('获取告警列表失败:', error)
        throw error
      })
  },

  // 获取实时告警
  getRealtimeAlerts: () => {
    return api.get('/alerts/realtime')
  },

  // 删除告警
  deleteAlert: (alertId) => {
    return api.delete(`/alerts/${alertId}`)
  },

  // 更新告警状态
  updateAlertStatus: (alertId, status, resolution_note = '') => {
    return api.put(`/alerts/${alertId}/status`, {
      status,
      resolution_note
    })
  },

  // 更新告警优先级
  updateAlertSeverity: (alertId, severity, reason = '') => {
    return api.put(`/alerts/${alertId}/severity`, {
      severity,
      reason
    })
  },

  // 创建告警
  createAlert: (data, onSuccess) => {
    // 获取用户信息和token
    const token = localStorage.getItem('token')
    if (!token) {
      console.error('未找到token，请先登录')
      return Promise.reject(new Error('未找到token，请先登录'))
    }

    // 构造最简单的告警数据，确保alert_type是数据库枚举中的有效值
    const alertData = {
      alert_type: 'container', // 使用数据库枚举中的有效值
      message: data.message || '系统告警',
      severity: 'high', // 枚举值: 'low', 'medium', 'high', 'critical'
      status: 'active', // 枚举值: 'active', 'acknowledged', 'resolved'
      details: JSON.stringify({timestamp: new Date().toISOString().substring(0, 19)})
    }
    
    console.log('创建告警 - 请求数据:', alertData)
    
    // 确保设置正确的headers
    return api.post('/alerts', alertData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        console.log('创建告警成功:', response)
        // 如果提供了成功回调函数，则调用它
        if (typeof onSuccess === 'function') {
          onSuccess(response);
        }
        return response
      })
      .catch(error => {
        console.error('创建告警失败:', error.response?.data || error)
        throw error
      })
  },

  // 获取告警设置
  getAlertSettings: () => {
    console.log('正在获取告警设置...')
    return api.get('/alerts/settings')
      .then(response => {
        console.log('获取到的告警设置:', response)
        if (response.success) {
          const settings = response.settings
          console.log(`数据来源: ${response.source}`)
          console.log(`CPU阈值: ${settings.thresholds.cpu}%`)
          console.log(`检查间隔: ${settings.checkInterval}分钟`)
          return {
            success: true,
            settings: settings,
            source: response.source
          }
        } else if (!response || !response.settings) {
          console.warn('告警设置为空，尝试从数据库获取...')
          return api.get('/alerts/settings/db')
            .then(dbResponse => {
              if (dbResponse.success) {
                console.log(`从数据库获取成功，数据来源: ${dbResponse.source}`)
                return {
                  success: true,
                  settings: dbResponse.settings,
                  source: 'mysql'
                }
              }
              throw new Error('无法获取告警设置')
            })
        }
        throw new Error('无效的响应格式')
      })
      .catch(error => {
        console.error('获取告警设置失败:', error)
        throw error
      })
  },

  // 更新告警设置
  updateAlertSettings: (settings) => {
    return api.post('/alerts/settings', settings)
  },

  // 检查服务器健康状态
  checkServerHealth: (serverId) => {
    return api.post('/alerts/server_health', { server_id: serverId })
  },

  // 检查Docker容器状态
  checkDockerStatus: (containerId) => {
    return api.post('/alerts/docker_container', { container_id: containerId })
  },

  // 检查流量告警
  checkTrafficAlert: (userId, limit) => {
    return api.post('/alerts/traffic', {
      user_id: userId,
      monthly_traffic_limit: limit
    })
  }
};

// 告警设置相关 API
const getAlertSettings = () => {
  return api.get('/alerts/settings')
}

const updateAlertSettings = (data) => {
  return api.post('/alerts/settings', data)
}

// 容器相关 API
const containerApi = {
  getContainers: () => {
    console.log('开始请求容器列表...')
    return api.get('/containers')
      .then(response => {
        console.log('原始API响应:', response)
        
        // 尝试从不同的响应结构中获取容器数据
        let containers = []
        
        if (Array.isArray(response)) {
          containers = response
        } else if (response && typeof response === 'object') {
          if (Array.isArray(response.data)) {
            containers = response.data
          } else if (response.containers && Array.isArray(response.containers)) {
            containers = response.containers
          } else if (response.result && Array.isArray(response.result)) {
            containers = response.result
          }
        }

        // 处理每个容器数据
        const processedContainers = containers.map(container => {
          try {
            if (!container.container_name) {
              console.warn('容器缺少container_name:', container)
              return null
            }

            // 从container_name中提取IP地址（仅用于日志）
            const ipMatch = container.container_name.match(/^(\d+)_(\d+)_(\d+)_(\d+)/)
            const ip = ipMatch ? ipMatch.slice(1, 5).join('.') : null
            
            if (!ip) {
              console.warn(`无法从容器名称提取IP地址: ${container.container_name}`)
              return null
            }

            // 确保容器有node_exporter_port
            if (!container.node_exporter_port) {
              console.warn(`容器缺少node_exporter_port: ${container.container_name}`)
              return null
            }

            return {
              ...container,
              ip: ip,
              metrics_port: container.node_exporter_port,
              // 使用后端代理路由，添加端口参数
              metrics_url: `/api/proxy/metrics/${encodeURIComponent(container.container_name)}?port=${container.node_exporter_port}`
            }
          } catch (err) {
            console.error('处理容器数据时出错:', err, container)
            return null
          }
        }).filter(Boolean)

        console.log('处理后的容器列表:', processedContainers)
        return processedContainers
      })
      .catch(error => {
        console.error('获取容器列表失败:', error)
        throw error
      })
  },

  // 获取容器监控数据
  getContainerMetrics: (containerName, port) => {
    console.log('开始获取容器监控数据:', containerName)
    // 使用后端代理路由获取监控数据，包含端口参数
    return api.get(`/proxy/metrics/${encodeURIComponent(containerName)}?port=${port}`, {
      headers: {
        'Accept': 'text/plain,*/*'  // 接受纯文本响应
      }
    })
      .then(response => {
        console.log('获取到监控数据:', response)
        if (!response || response.error) {
          throw new Error(response?.error || '获取监控数据失败')
        }
        return response
      })
      .catch(error => {
        console.error('获取监控数据失败:', error)
        throw error
      })
  }
}

export default {
  ...dashboardApi,
  trafficApi,
  alertApi,
  containerApi,  // 确保 containerApi 被正确导出
  // 用户相关 API
  login(email, password) {
    return api.post('/login', { email, password })
  },
  
  addUser(userData) {
    return api.post('/api/add_user', userData)
  },
  
  sendVerificationEmail(email) {
    return api.post('/send_verification_email', { email })
  },
  
  getRentalInfo() {
    return api.get('/rental/history/' + JSON.parse(localStorage.getItem('user'))?.id)
  },
  
  getUserHistory(userId) {
    return api.get(`/user/history/${userId}`)
  },
  
  applyDistributor(userId, distributorCode) {
    return api.post('/user/apply_distributor', { user_id: userId, distributor_code: distributorCode })
  },
  
  downloadAcl() {
    return api.get('/user/download_acl')
  },

  // 新增的获取所有用户的方法
  getAllUsers() {
    return api.get('/users').then(response => {
      console.log('API Response:', response) // 添加日志
      return response
    })
  },

  // 服务器相关 API
  getServers,
  getServerCategories,
  addServer,
  deleteServer,
  updateServer,
  getServerHealthCheck,

  // 日志相关 API
  getSystemLogs() {
    return api.get('/logs/system')
  },
  
  getUserLogsByTime() {
    return api.get('/logs/user_by_time')
  },
  
  updateLog(id, data) {
    return api.put(`/logs/update/${id}`, data)
  },
  
  deleteLog(id) {
    return api.delete(`/logs/delete/${id}`)
  },
  // 容器相关 API
  getContainers() {
    return api.get('/containers')
  },
  
  createContainer(data) {
    return api.post('/containers', data)
  },
  
  getContainerStatus(containerName) {
    return api.get(`/containers/${containerName}/status`)
  },
  
  stopContainer(containerName) {
    return api.post(`/containers/${containerName}/stop`)
  },
  
  updateContainer(containerName, data) {
    return api.put(`/containers/${containerName}`, data)
  },
  // ACL 相关 API
  generateAcl,
  getAclLogs,
  downloadAcl,
  getAclList,
  getUser,
  getServer,
  getContainer,
  getAclConfigs,
  getServerContainers,

  // 流量相关 API
  getRealTimeTraffic() {
    return api.get('/traffic/realtime')
  },
  
  getContainerTraffic(containerId) {
    return api.get(`/traffic/realtime/${containerId}`)
  },
  
  getTrafficHistory(userId) {
    return api.get(`/traffic/history/${userId}`)
  },
  
  getTrafficStats(startDate, endDate) {
    return api.post('/traffic/stats', { start_date: startDate, end_date: endDate })
  },
  
  getOverlimitUsers() {
    return api.get('/traffic/overlimit')
  },

  // 租赁相关 API
  checkRentalExpiry() {
    return api.get('/rental/check_expiry')
  },
  createRental(data) {
    return api.post('/rental/create', data);
  },

  sendExpiryNotifications(userId, expiryDate) {
    return api.post('/rental/send_expiry_notifications', { user_id: userId, expiry_date: expiryDate })
  },
  
  renewRental(data) {
    return api.post('/rental/renew', data)
      .then(response => {
        console.log('续费响应:', response)
        return response.data
      })
      .catch(error => {
        console.error('续费失败:', error)
        throw error
      })
  },
  
  deleteRental(serialId) {
    return api.delete(`/rental/delete/${serialId}`)
  },

  // 序列号相关 API
  getSerialList() {
    return api.get('/serial/list')
  },
  checkSerial(serialCode) {
    return api.get(`/serial/check/${serialCode}`)
  },
  generateSerial(data) {
    return api.post('/serial/generate', data)
  },
  updateSerial(id, data) {
    return api.put(`/serial/update/${id}`, data)
  },
  deleteSerial(id) {
    return api.delete(`/serial/delete/${id}`)
  },

  // 高可用性相关 API
  getHaHealth() {
    return api.get('/ha/health')
  },
  
  getServerHealth(serverId) {
    return api.get(`/ha/health/${serverId}`)
  },
  
  getHaContainerTraffic(containerId) {
    return api.get(`/ha/container_traffic/${containerId}`)
  },
  
  startFailover() {
    return api.post('/ha/failover')
  },
  
  startLoadBalance() {
    return api.post('/ha/load_balance')
  },
  
  startDisasterRecovery() {
    return api.post('/ha/disaster_recovery')
  },
  
  replaceContainer() {
    return api.post('/ha/replace_container')
  },

  // 通知相关 API
  sendReminderNotification(data) {
    return api.post('/rental/send_expiry_notifications', {
      days_to_expiry: data.days_to_expiry,
      user_id: data.user_id,
      expiry_date: data.expiry_date,
      email: data.email
    })
  },

  // 监控相关 API
  getMonitoringStatus() {
    return api.get('/monitoring')
  },

  // 安全相关 API
  getUserAclInfo(userId) {
    return api.get(`/security/user_acl_info/${userId}`)
  },

  // API 列表
  getApiUrls() {
    return api.get('/api/urls')
  },

  // 用户相关补充
  getUserAclInfo(userId) {
    return api.get(`/user/acl_info/${userId}`)
  },

  // 租赁历史相关补充
  getRentalHistory(userId) {
    return api.get(`/rental/history/${userId}`)
  },
  updateRentalHistory(id, data) {
    return api.put(`/rental/history/update/${id}`, data)
  },
  deleteRentalHistory(id) {
    return api.delete(`/rental/history/delete/${id}`)
  },

  // 通知相关补充
  getNotifications() {
    return api.get('/notifications')
  },
  markNotificationAsRead(notificationId) {
    return api.put(`/notifications/${notificationId}/read`)
  },

  // 序列号相关 API
  getSerials,
  generateSerials,
  deleteSerial,
  batchDeleteSerials,

  sendVerificationCode(email) {
    return api.post('/send_verification_code', { email })
  },

  //getTrafficData
  saveTrafficData,

  // 获取ACL日志
  getAclLogs() {
    return api.get('/acl/logs').then(response => {
      console.log('Raw response:', response)
      
      // 检查响应数据结构
      if (!response || !response.logs) {
        console.warn('No logs data in response')
        return { logs: [], success: false }
      }

      // 返回标准化的响应格式
      return {
        logs: response.logs || [],
        success: !!response.success
      }
    }).catch(error => {
      console.error('获取ACL日志失败:', error)
      return { logs: [], success: false }
    })
  },

  // 更新个人资料
  updateProfile(data) {
    return api.post('/user/update_info', data)
  },

  // 获取告警设置
  getAlertSettings,
  
  // 更新告警设置
  updateAlertSettings,
} 
