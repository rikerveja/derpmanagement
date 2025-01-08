import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://100.82.38.13:8000/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
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

export default {
  // 用户相关 API
  login(email, password) {
    return api.post('/login', { email, password })
  },
  
  addUser(userData) {
    return api.post('/add_user', userData)
  },
  
  sendVerificationEmail(email) {
    return api.post('/send_verification_email', { email })
  },
  
  getRentalInfo() {
    return api.get('/user/rental_info')
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
  addServer(serverData) {
    return api.post('/add_server', serverData)
  },
  
  getServerStatus(serverId) {
    return api.get(`/server/status/${serverId}`)
  },
  
  checkServerHealth() {
    return api.get('/server/health_check')
  },

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
  generateAcl(userId, permissions) {
    return api.post('/acl/generate', { user_id: userId, permissions })
  },
  
  updateAcl(userId, permissions) {
    return api.post('/acl/update', { user_id: userId, permissions })
  },
  
  getAclLogs(userId) {
    return api.get(`/acl/logs/${userId}`)
  },
  
  downloadUserAcl(username) {
    return api.get(`/acl/download/${username}`)
  },

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
  
  sendExpiryNotifications(userId, expiryDate) {
    return api.post('/rental/send_expiry_notifications', { user_id: userId, expiry_date: expiryDate })
  },
  
  renewRental(rentalId, newExpiryDate) {
    return api.post('/rental/renew', { rental_id: rentalId, new_expiry_date: newExpiryDate })
  },
  
  deleteRental(serialId) {
    return api.delete(`/rental/delete/${serialId}`)
  },

  // 告警相关 API
  getAlerts() {
    return api.get('/alerts')
  },
  
  addAlert(alertData) {
    return api.post('/alerts/add', alertData)
  },
  
  checkMonthlyTraffic(month) {
    return api.post('/alerts/traffic', { month })
  },
  
  checkServerHealthStatus(serverId) {
    return api.post('/alerts/server_health', { server_id: serverId })
  },
  
  checkDockerTraffic(containerId) {
    return api.post('/alerts/docker_traffic', { container_id: containerId })
  },
  
  checkDockerContainer(containerId) {
    return api.post('/alerts/docker_container', { container_id: containerId })
  },
  
  deleteAlert(id) {
    return api.delete(`/alerts/delete/${id}`)
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
    return api.post('/notifications/send_reminder', data)
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

  // 服务器相关补充
  getServerHealthCheck(serverId) {
    return api.get(`/server/health_check/${serverId}`)
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
  batchDeleteSerials
} 
