<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import BaseDialogR from '@/components/BaseDialogR.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import { mdiInformation, mdiCheckCircle, mdiAlertCircle, mdiCircleOutline } from '@mdi/js'
import api from '@/services/api'
import SearchSelect from '@/components/SearchSelect.vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'create'])

// 数据列表
const serialList = ref([])      // 序列号列表
const userList = ref([])        // 用户列表
const serverList = ref([])      // 服务器列表
const containerList = ref([])   // 容器列表
const aclList = ref([])         // ACL列表

// 加载状态
const loading = ref({
  serials: false,
  users: false,
  servers: false,
  containers: false,
  acl: false
})

// 表单数据
const rentalForm = ref({
  serial_code: '',
  user_id: '',
  traffic_limit: 0,
  server_id: null,
  container_id: null,
  container_config: {
    bandwidth_limit: 100
  }
})

// 选中的数据
const selectedSerial = ref(null)
const selectedServer = ref(null)
const selectedContainer = ref(null)
const selectedUser = ref(null)

// 获取序列号列表
const fetchSerials = async () => {
  try {
    loading.value.serials = true
    const response = await api.getSerials()
    console.log('序列号列表响应:', response)
    if (response && response.serial_numbers) {
      serialList.value = response.serial_numbers
        .filter(serial => serial.status === 'unused')
        .map(serial => ({
          ...serial,
          label: `${serial.serial_code} ${serial.type ? `- ${serial.type}` : ''}`
        }))
    }
  } catch (error) {
    console.error('获取序列号列表失败:', error)
    errors.value.serial = '获取序列号列表失败'
  } finally {
    loading.value.serials = false
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value.users = true
    
    // 1. 首先获取所有租赁信息来确定已有租赁的用户
    const rentalsResponse = await api.getRentals()
    if (rentalsResponse.success && Array.isArray(rentalsResponse.rentals)) {
      existingUserIds.value = rentalsResponse.rentals
        .filter(rental => rental.status === 'active') // 只过滤活跃的租赁
        .map(rental => rental.user_id)
    }
    
    // 2. 获取用户列表
    const response = await api.getAllUsers()
    console.log('获取到的用户数据:', response)
    
    let allUsers = []
    if (Array.isArray(response)) {
      allUsers = response
    } else if (response?.users) {
      allUsers = response.users
    } else if (response?.data) {
      allUsers = response.data
    }

    // 3. 过滤掉已有租赁的用户
    userList.value = allUsers
      .filter(user => !existingUserIds.value.includes(user.id))
      .map(user => ({
        id: user.id,
        value: user.id,
        username: user.username,
        email: user.email,
        label: `${user.username} (${user.email})`
      }))

  } catch (error) {
    console.error('获取用户列表失败:', error)
    errors.value.user = '获取用户列表失败'
  } finally {
    loading.value.users = false
  }
}

// 获取服务器列表
const fetchServers = async () => {
  try {
    loading.value.servers = true
    console.log('正在获取服务器列表...')
    const response = await api.getServers()
    console.log('服务器列表响应:', response)
    
    if (response.success) {
      const allServers = response.servers
      console.log('所有服务器:', allServers)

      serverList.value = allServers
        .filter(server => server.status === 'healthy')
        .map(server => ({
          ...server,
          // 修正字段名：cpu -> cpu_total, memory -> memory_total
          cpu_available: server.cpu || 0,
          cpu_total: server.cpu || 0,
          memory_available: server.memory || 0,
          memory_total: server.memory || 0,
          label: `${server.server_name} (${server.ip_address}) - 区域: ${server.region} - CPU: ${server.cpu || 0} | 内存: ${server.memory || 0}GB`
        }))
    }
  } catch (error) {
    console.error('获取服务器列表失败:', error)
    errors.value.server = '获取服务器列表失败: ' + error.message
  } finally {
    loading.value.servers = false
  }
}

// 获取容器列表
const fetchContainers = async (serverId) => {
  if (!serverId) return
  try {
    loading.value.containers = true
    const response = await api.getServerContainers(serverId)
    
    if (response.success && response.containers) {
      // 过滤出属于当前服务器的容器
      containerList.value = response.containers
        .filter(container => container.server_id === serverId && container.status === 'running')
        .map(container => ({
          id: container.id,
          container_id: container.container_id,
          container_name: container.container_name,
          cpu: container.cpu || 1,
          memory: container.memory || 1024,
          bandwidth: container.bandwidth || 100,
          status: container.status
        }))
    }
  } catch (error) {
    console.error('获取容器列表失败:', error)
    errors.value.container = '获取容器列表失败: ' + error.message
    containerList.value = []
  } finally {
    loading.value.containers = false
  }
}

// 获取ACL列表
const fetchAcl = async () => {
  try {
    loading.value.acl = true
    const response = await api.getAclConfigs()
    if (response.success) {
      aclList.value = response.acl_configs
    }
  } catch (error) {
    console.error('获取ACL列表失败:', error)
  } finally {
    loading.value.acl = false
  }
}

// 选择序列号
const handleSerialSelect = (serial) => {
  if (!serial) return
  selectedSerial.value = serial
  rentalForm.value.serial_code = serial.serial_code

  // 从序列号中提取流量限制
  const trafficCode = serial.serial_code.slice(4, 7) // 假设序列号格式为030D05G
  rentalForm.value.traffic_limit = trafficCode === '05G' ? 5 : 10
}

// 选择服务器
const handleServerSelect = async (server) => {
  if (!server) return
  selectedServer.value = server
  rentalForm.value.server_id = server.id || server.server_id
  
  // 清空之前的容器选择
  selectedContainer.value = null
  rentalForm.value.container_id = null
  containerList.value = []
  
  // 获取该服务器的容器列表
  await fetchContainers(server.id || server.server_id)
}

// 选择容器
const handleContainerSelect = (container) => {
  if (!container) {
    selectedContainer.value = null
    rentalForm.value.container_id = null
    return
  }
  
  console.log('选择容器:', container)
  selectedContainer.value = container
  rentalForm.value.container_id = container.id || container.container_id

  // 创建 ACL 配置
  createAclConfig()
}

// 创建 ACL 配置
const createAclConfig = async () => {
  if (!selectedContainer.value) return

  try {
    loading.value.acl = true
    console.log('正在创建 ACL 配置...')

    const aclConfig = {
      name: `${selectedContainer.value.container_name}_acl`,
      description: `ACL for container ${selectedContainer.value.container_name}`,
      rules: [
        {
          type: 'allow',
          protocol: 'tcp',
          port_range: '1-65535',
          source: '0.0.0.0/0'
        }
      ]
    }

    const response = await api.createAclConfig(aclConfig)
    console.log('ACL 配置创建响应:', response)

    if (response.success) {
      rentalForm.value.acl_id = response.acl_config.id
      console.log('ACL 配置已创建, ID:', rentalForm.value.acl_id)
    } else {
      throw new Error(response.message || '创建 ACL 配置失败')
    }
  } catch (error) {
    console.error('创建 ACL 配置失败:', error)
    errors.value.acl = '创建 ACL 配置失败: ' + error.message
  } finally {
    loading.value.acl = false
  }
}

// 重置表单和状态
const resetForm = () => {
  // 重置表单数据
  rentalForm.value = {
    serial_code: '',
    user_id: '',
    traffic_limit: 0,
    server_id: null,
    container_id: null,
    acl_id: null,
    container_config: {
      bandwidth_limit: 100
    }
  }
  
  // 重置选中状态
  selectedSerial.value = null
  selectedServer.value = null
  selectedContainer.value = null
  
  // 清空列表数据
  containerList.value = []
  
  // 重置错误状态
  errors.value = {}
  serialSearchQuery.value = ''  // 重置搜索框
  showSerialDropdown.value = false  // 关闭下拉列表
}

// 处理关闭
const handleClose = () => {
  resetForm()
  emit('close')
}

// 监听对话框显示状态
watch(() => props.show, async (newVal) => {
  if (newVal) {
    // 使用 nextTick 避免递归更新
    await nextTick()
    try {
      // 分开加载数据，避免同时触发多个更新
      await fetchSerials()
      await fetchUsers()
    } catch (error) {
      console.error('初始化数据失败:', error)
    }
  } else {
    // 关闭时重置
    resetForm()
  }
})

// 添加错误状态对象
const errors = ref({
  serial: '',
  user: '',
  server: '',
  container: '',
  acl: '',
  form: ''
})

// 添加表单验证
const validateForm = () => {
  return isAllSelected.value
}

// 添加用户选择处理函数
const handleUserSelect = (user) => {
  // 检查用户是否已有租赁
  if (existingUserIds.value.includes(user.id)) {
    alert('该用户已有租赁，请选择其他用户')
    selectedUser.value = null
    rentalForm.value.user_id = ''
    return
  }

  rentalForm.value.user_id = user.id
  selectedUser.value = user
}

// 创建一个提交锁
const submitLock = ref(false);

// 创建租赁
const handleCreate = async () => {
  if (!isAllSelected.value || loading.value.create) return
  
  try {
    loading.value.create = true
    console.log('准备创建租赁，数据:', rentalForm.value) // 添加日志
    
    const response = await api.createRental(rentalForm.value)
    console.log('创建租赁响应:', response) // 添加日志
    
    if (response.success) {
      // 修改这里：确保发送正确的数据
      emit('create', response.rental) // 确保 response.rental 包含新创建的租赁数据
      handleClose()
    } else {
      throw new Error(response.message || '创建失败')
    }
  } catch (error) {
    console.error('创建租赁失败:', error)
    alert('创建租赁失败: ' + error.message)
  } finally {
    loading.value.create = false
  }
}

// 添加错误显示计算属性
const showError = computed(() => {
  return Object.values(errors.value).some(error => error !== '')
})

// 初始化数据
onMounted(async () => {
  await fetchUsers() // 确保先获取用户列表
  await Promise.all([
    fetchSerials(),
    fetchServers(),
    fetchAcl()
  ])
})

// 在 script setup 中添加
const serialSearchQuery = ref('')
const showSerialDropdown = ref(false)

// 过滤序列号列表
const filteredSerials = computed(() => {
  const query = serialSearchQuery.value.toLowerCase().trim()
  if (!query) return serialList.value
  
  return serialList.value.filter(serial => 
    serial.serial_code.toLowerCase().includes(query) ||
    serial.label.toLowerCase().includes(query)
  )
})

// 处理序列号搜索
const handleSerialSearch = async () => {
  showSerialDropdown.value = true
  const query = serialSearchQuery.value.toLowerCase().trim()
  
  // 如果输入的是完整的序列号，直接验证并选择
  const exactMatch = serialList.value.find(
    serial => serial.serial_code.toLowerCase() === query
  )
  
  if (exactMatch) {
    await selectSerial(exactMatch)
  }
}

// 选择序列号
const selectSerial = async (serial) => {
  selectedSerial.value = serial
  serialSearchQuery.value = serial.serial_code
  showSerialDropdown.value = false
  await handleSerialSelect(serial)
}

// 点击外部关闭下拉列表
const closeDropdown = (e) => {
  if (!e.target.closest('.form-group')) {
    showSerialDropdown.value = false
  }
}

// 添加点击外部关闭下拉列表的事件监听
onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})

// 搜索查询和下拉状态
const searchQueries = ref({
  serial: '',
  user: '',
  server: ''
})

const dropdownStates = ref({
  serial: false,
  user: false,
  server: false
})

// 过滤后的列表
const filteredLists = computed(() => ({
  serial: serialList.value.filter(item => 
    item.serial_code.toLowerCase().includes(searchQueries.value.serial.toLowerCase())
  ),
  user: userList.value.filter(item =>
    item.label.toLowerCase().includes(searchQueries.value.user.toLowerCase())
  ),
  server: serverList.value.filter(item =>
    (item.server_name + item.ip_address + item.region)
      .toLowerCase()
      .includes(searchQueries.value.server.toLowerCase())
  )
}))

// 处理搜索输入
const handleSearch = (type) => {
  dropdownStates.value[type] = true
}

// 选择处理函数
const handleSelect = async (type, item) => {
  switch(type) {
    case 'serial':
      await handleSerialSelect(item)
      break
    case 'user':
      rentalForm.value.user_id = item.id
      selectedUser.value = item
      break
    case 'server':
      await handleServerSelect(item)
      break
  }
  searchQueries.value[type] = ''
  dropdownStates.value[type] = false
}

// 添加 aclContent ref
const aclContent = ref(null)

// 监听容器选择变化，自动生成 ACL
watch(selectedContainer, async (newContainer) => {
  if (newContainer) {
    console.log('容器选择变更:', newContainer)
    rentalForm.value.container_id = newContainer.id || newContainer.container_id
    
    // 开始生成 ACL
    try {
      loading.value.acl = true
      const response = await api.generateAcl({
        user_id: rentalForm.value.user_id,
        server_id: selectedServer.value.id,
        container_ids: [rentalForm.value.container_id]
      })
      
      if (response.success) {
        rentalForm.value.acl_id = response.acl_id
        // 直接保存完整的 ACL 响应数据
        aclContent.value = response
        console.log('ACL 生成成功，完整数据:', response)
      } else {
        errors.value.acl = response.message || '生成 ACL 失败'
      }
    } catch (error) {
      console.error('生成 ACL 失败:', error)
      errors.value.acl = error.message || '生成 ACL 失败'
    } finally {
      loading.value.acl = false
    }
  }
})

// 添加检查所有必选项是否已选择的计算属性
const isAllSelected = computed(() => {
  // 首先检查用户选择是否有效
  if (!selectedUser.value || existingUserIds.value.includes(selectedUser.value.id)) {
    return false
  }

  // 其他必要字段的验证
  return !!(
    selectedSerial.value &&
    selectedUser.value &&
    selectedServer.value &&
    selectedContainer.value &&
    rentalForm.value.traffic_limit > 0
  )
})

// 在组件挂载时获取数据
onMounted(async () => {
  await fetchUsers() // 确保先获取用户列表
  await Promise.all([
    fetchSerials(),
    fetchServers(),
    fetchAcl()
  ])
})

// 监听用户选择变化
watch(selectedUser, (newUser) => {
  if (newUser && existingUserIds.value.includes(newUser.id)) {
    // 如果选择了已有租赁的用户，清空后续选择
    selectedServer.value = null
    selectedContainer.value = null
    rentalForm.value.server_id = null
    rentalForm.value.container_id = null
    errors.value.user = '该用户已有租赁，请选择其他用户'
  } else {
    errors.value.user = ''
  }
})

// 在 script setup 中添加
const existingUserIds = ref([]) // 存储已有租赁的用户ID

// 添加步骤状态控制
const stepsEnabled = computed(() => ({
  serial: true, // 序列号始终可选
  user: !!selectedSerial.value, // 选择序列号后才能选择用户
  server: !!(selectedSerial.value && selectedUser.value && !existingUserIds.value.includes(selectedUser.value.id)), // 选择用户后才能选择服务器
  container: !!(selectedSerial.value && selectedUser.value && selectedServer.value && !existingUserIds.value.includes(selectedUser.value.id)), // 选择服务器后才能选择容器
  acl: !!(selectedSerial.value && selectedUser.value && selectedServer.value && selectedContainer.value && !existingUserIds.value.includes(selectedUser.value.id)) // 选择容器后才能配置ACL
}))
</script>

<template>
  <BaseDialogR
    :show="show"
    @close="handleClose"
  >
    <template #header>
      <div class="text-lg font-bold">创建租赁</div>
    </template>

    <template #default>
      <!-- 已选信息展示区域 -->
      <div v-if="selectedSerial || selectedUser || selectedServer || selectedContainer" 
           class="mb-6 bg-white border border-gray-200 rounded-lg shadow-sm">
        <div class="border-b border-gray-200 bg-gray-50 px-4 py-3">
          <h3 class="font-medium text-gray-700">已选择信息</h3>
        </div>
        
        <div class="p-4 space-y-3">
          <!-- 序列号信息 -->
          <div v-if="selectedSerial" class="flex items-start p-2 hover:bg-gray-50 rounded-md">
            <div class="flex-shrink-0 w-24">
              <span class="font-medium text-gray-600">序列号</span>
            </div>
            <div class="flex-grow">
              <div class="font-medium text-gray-800">{{ selectedSerial.serial_code }}</div>
              <div class="text-sm text-gray-500">类型: {{ selectedSerial.type || '标准版' }}</div>
            </div>
            <BaseIcon :path="mdiCheckCircle" class="text-green-500 flex-shrink-0" size="20" />
          </div>

          <!-- 用户信息 -->
          <div v-if="selectedUser" class="flex items-start p-2 hover:bg-gray-50 rounded-md">
            <div class="flex-shrink-0 w-24">
              <span class="font-medium text-gray-600">用户</span>
            </div>
            <div class="flex-grow">
              <div class="font-medium text-gray-800">{{ selectedUser.username }}</div>
              <div class="text-sm text-gray-500">{{ selectedUser.email }}</div>
            </div>
            <BaseIcon :path="mdiCheckCircle" class="text-green-500 flex-shrink-0" size="20" />
          </div>

          <!-- 服务器信息 -->
          <div v-if="selectedServer" class="flex items-start p-2 hover:bg-gray-50 rounded-md">
            <div class="flex-shrink-0 w-24">
              <span class="font-medium text-gray-600">服务器</span>
            </div>
            <div class="flex-grow">
              <div class="font-medium text-gray-800">{{ selectedServer.server_name }}</div>
              <div class="text-sm text-gray-500">IP: {{ selectedServer.ip_address }}</div>
              <div class="text-sm text-gray-500">区域: {{ selectedServer.region }}</div>
            </div>
            <BaseIcon :path="mdiCheckCircle" class="text-green-500 flex-shrink-0" size="20" />
          </div>

          <!-- 容器信息 -->
          <div v-if="selectedContainer" class="flex items-start p-2 hover:bg-gray-50 rounded-md">
            <div class="flex-shrink-0 w-24">
              <span class="font-medium text-gray-600">容器</span>
            </div>
            <div class="flex-grow">
              <div class="font-medium text-gray-800">{{ selectedContainer.container_name }}</div>
              <div class="text-sm text-gray-500">镜像: zhangjiayuan1983/ip_derper:latest</div>
            </div>
            <BaseIcon :path="mdiCheckCircle" class="text-green-500 flex-shrink-0" size="20" />
          </div>

          <!-- ACL配置信息 -->
          <div v-if="aclContent" class="border-t border-gray-200 mt-3 pt-4">
            <div class="flex items-center px-2 mb-2">
              <span class="font-medium text-gray-700">ACL 配置信息</span>
              <BaseIcon :path="mdiCheckCircle" class="ml-2 text-green-500" size="20" />
            </div>
            <div class="bg-gray-50 p-4 rounded-md">
              <pre class="whitespace-pre-wrap text-xs overflow-x-auto text-gray-600">{{ JSON.stringify(aclContent, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 原有的表单内容 -->
      <div class="space-y-4">
        <!-- 步骤提示 -->
        <div class="space-y-2 mb-6">
          <div class="flex items-center" :class="{'text-green-600': selectedSerial, 'text-gray-400': !selectedSerial}">
            <BaseIcon :path="selectedSerial ? mdiCheckCircle : mdiCircleOutline" class="mr-2" />
            <span>1. 选择序列号</span>
          </div>
          <div class="flex items-center" :class="{'text-green-600': rentalForm.user_id, 'text-gray-400': !rentalForm.user_id}">
            <BaseIcon :path="rentalForm.user_id ? mdiCheckCircle : mdiCircleOutline" class="mr-2" />
            <span>2. 选择用户</span>
          </div>
          <div class="flex items-center" :class="{'text-green-600': selectedServer, 'text-gray-400': !selectedServer}">
            <BaseIcon :path="selectedServer ? mdiCheckCircle : mdiCircleOutline" class="mr-2" />
            <span>3. 选择服务器</span>
          </div>
          <div class="flex items-center" :class="{'text-green-600': selectedContainer, 'text-gray-400': !selectedContainer}">
            <BaseIcon :path="selectedContainer ? mdiCheckCircle : mdiCircleOutline" class="mr-2" />
            <span>4. 选择容器</span>
          </div>
          <div class="flex items-center" :class="{'text-green-600': aclContent, 'text-gray-400': !aclContent}">
            <BaseIcon :path="aclContent ? mdiCheckCircle : mdiCircleOutline" class="mr-2" />
            <span>5. 配置 ACL 规则</span>
          </div>
        </div>

        <!-- 序列号选择 -->
        <SearchSelect
          label="序列号"
          :items="serialList"
          :loading="loading.serials"
          :error="errors.serial"
          @select="handleSerialSelect"
        >
          <template #item="{ item }">
            {{ item.serial_code }} {{ item.type ? `- ${item.type}` : '' }}
          </template>
        </SearchSelect>

        <!-- 流量限制显示 -->
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">流量限制</label>
          <input
            v-model="rentalForm.traffic_limit"
            type="number"
            class="form-input"
            placeholder="输入流量限制"
          />
          <span class="text-sm text-gray-500">GB</span>
        </div>

        <!-- 用户选择 -->
        <SearchSelect
          label="用户"
          :items="userList"
          :loading="loading.users"
          :error="errors.user"
          @select="handleUserSelect"
          :disabled="!stepsEnabled.user"
        >
          <template #item="{ item }">
            <div class="flex flex-col">
              <span class="font-medium">{{ item.username }}</span>
              <span class="text-sm text-gray-500">{{ item.email }}</span>
            </div>
          </template>
        </SearchSelect>

        <!-- 服务器选择 -->
        <SearchSelect
          label="服务器"
          :items="serverList"
          :loading="loading.servers"
          :error="errors.server"
          @select="handleServerSelect"
          :disabled="!stepsEnabled.server"
        >
          <template #item="{ item }">
            {{ item.server_name || item.ip_address }} ({{ item.ip_address }}) - 
            区域: {{ item.region }} - 
            CPU: {{ item.cpu || 0 }} | 
            内存: {{ item.memory || 0 }}GB
          </template>
        </SearchSelect>

        <!-- 容器选择 -->
        <div class="form-group" v-if="selectedServer">
          <label class="block text-sm font-medium mb-2">容器 <span class="text-red-500">*</span></label>
          <div class="relative">
            <select
              v-model="selectedContainer"
              class="form-input"
              required
              :disabled="!stepsEnabled.container"
            >
              <option value="">请选择容器</option>
              <option 
                v-for="container in containerList" 
                :key="container.id || container.container_id" 
                :value="container"
              >
                {{ container.container_name }} - 
                CPU: {{ container.cpu }}核 | 
                内存: {{ container.memory }}MB | 
                带宽: {{ container.bandwidth }}Mbps
              </option>
            </select>
            <div v-if="loading.containers" class="absolute right-2 top-2">
              <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent"></div>
            </div>
          </div>
          <div v-if="errors.container" class="mt-1 text-sm text-red-600">
            {{ errors.container }}
          </div>
          <div v-if="!stepsEnabled.container" class="mt-1 text-sm text-yellow-600">
            请先选择用户和服务器
          </div>
        </div>

        <!-- 在容器选择后添加 ACL 状态显示 -->
        <div v-if="selectedContainer" class="form-group">
          <label class="block text-sm font-medium mb-2">ACL 配置</label>
          <div class="relative space-y-2">
            <!-- ACL 生成状态 -->
            <div v-if="loading.acl" class="flex items-center text-blue-600">
              <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent mr-2"></div>
              <span>正在生成 ACL 配置...</span>
            </div>
            
            <!-- ACL 配置内容 -->
            <div v-else-if="rentalForm.acl_id" class="space-y-2">
              <div class="flex items-center text-green-600">
                <BaseIcon :path="mdiCheckCircle" class="mr-2" />
                <span>ACL 配置已生成</span>
              </div>
              
              <!-- ACL 详细内容 -->
              <div v-if="aclContent" class="bg-gray-50 p-4 rounded-lg">
                <div class="text-sm space-y-2">
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <span class="font-medium">区域名称:</span>
                      <span class="ml-2">{{ aclContent.acl?.RegionName || '-' }}</span>
                    </div>
                    <div>
                      <span class="font-medium">DERP端口:</span>
                      <span class="ml-2">{{ aclContent.acl?.DERPPort || '-' }}</span>
                    </div>
                    <div>
                      <span class="font-medium">节点名称:</span>
                      <span class="ml-2">{{ aclContent.acl?.Name || '-' }}</span>
                    </div>
                    <div>
                      <span class="font-medium">IPv4地址:</span>
                      <span class="ml-2">{{ aclContent.acl?.ipv4 || '-' }}</span>
                    </div>
                  </div>
                  
                  <!-- ACL 规则 -->
                  <div class="mt-2">
                    <div class="font-medium mb-1">ACL 规则:</div>
                    <div class="bg-gray-100 p-2 rounded text-xs">
                      <div v-if="aclContent.acl?.rules?.length">
                        <div v-for="(rule, index) in aclContent.acl.rules" :key="index" class="mb-1">
                          <div>类型: {{ rule.type }}</div>
                          <div>协议: {{ rule.protocol }}</div>
                          <div>端口范围: {{ rule.port_range }}</div>
                          <div>源地址: {{ rule.source }}</div>
                        </div>
                      </div>
                      <div v-else>暂无规则</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 错误信息 -->
            <div v-else-if="errors.acl" class="text-red-600 flex items-center">
              <BaseIcon :path="mdiAlertCircle" class="mr-2" />
              <span>{{ errors.acl }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          type="button"
          color="info"
          label="取消"
          @click="handleClose"
          :disabled="loading.create"
        />
        <BaseButton
          type="button"
          color="success"
          :label="loading.create ? '创建中...' : '创建'"
          @click="handleCreate"
          :disabled="!isAllSelected || loading.create"
          :loading="loading.create"
        />
      </div>
    </template>
  </BaseDialogR>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

.form-input {
  @apply w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}

/* 添加禁用状态样式 */
.form-input:disabled {
  @apply bg-gray-100 cursor-not-allowed;
}

/* 添加加载动画样式 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* ACL 内容显示样式 */
pre {
  max-width: 100%;
  overflow-x: auto;
  font-size: 0.75rem;
  line-height: 1.25;
}

.bg-gray-50 {
  max-height: 300px;
  overflow-y: auto;
}

/* 添加滚动条样式 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.400') theme('colors.gray.100');
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded hover:bg-gray-500;
}

/* 添加禁用状态的样式 */
.form-input:disabled,
.search-select:disabled {
  @apply bg-gray-100 cursor-not-allowed opacity-60;
}

/* 添加步骤提示的禁用状态样式 */
.step-disabled {
  @apply opacity-50 cursor-not-allowed;
}
</style> 
