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
      window.location.href = '/#/login'
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

export default {
  ...dashboardApi,
  trafficApi,  // 直接导出 trafficApi 对象
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

  // 告警相关 API
  getAlerts() {
    return api.get('/alerts/all')
      .then(response => response.data)
  },
  
  getRealtimeAlerts() {
    return api.get('/alerts/realtime')
      .then(response => response.data)
  },
  
  addAlert(data) {
    return api.post('/alerts/add', data)
      .then(response => response.data)
  },
  
  deleteAlert(id) {
    return api.delete(`/alerts/delete/${id}`)
      .then(response => response.data)
  },
  
  checkServerHealth(serverId) {
    return api.post('/alerts/server_health', { server_id: serverId })
      .then(response => response.data)
  },
  
  checkDockerStatus(containerId) {
    return api.post('/alerts/docker_container', { container_id: containerId })
      .then(response => response.data)
  },
  
  checkTrafficAlert(userId, limit) {
    return api.post('/alerts/traffic', {
      user_id: userId,
      monthly_traffic_limit: limit
    }).then(response => response.data)
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
      user_id: data.user_id
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
  getAlertSettings() {
    return api.get('/alerts/settings')
      .then(response => response.data)
  },
  
  // 更新告警设置
  updateAlertSettings(settings) {
    return api.post('/alerts/settings/update', settings)
      .then(response => response.data)
  },
} 
