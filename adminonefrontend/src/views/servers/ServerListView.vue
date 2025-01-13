<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiServer,
  mdiPlus,
  mdiDelete,
  mdiRefresh,
  mdiPencil,
  mdiMagnify,
  mdiFilter,
  mdiHeartPulse
} from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseDialog from '@/components/BaseDialog.vue'
import api from '@/services/api'

// 服务器列表数据
const servers = ref([])
const categories = ref([]) // 服务器分类
const regions = ref([
  '上海', '深圳', '北京', '广州', '杭州', 
  '成都', '武汉', '南京', '天津', '重庆',
  '西安', '青岛', '长沙'
])

// 分页
const currentPage = ref(1)
const itemsPerPage = 10

// 筛选
const searchQuery = ref('')
const selectedCategoryId = ref('all')  // 改为 categoryId
const selectedRegion = ref('all')
const selectedStatus = ref('all')

// 服务器表单
const serverForm = ref({
  server_name: '',
  ip_address: '',
  region: '上海',
  cpu: 2,
  memory: 2,
  storage: 40,
  category_id: '',
  bandwidth: 100,
  user_count: 0,
  total_traffic: 20
})

// 服务器分类默认值
const defaultCategories = [
  { id: 1, category_name: '4坑位版' },
  { id: 2, category_name: '2坑位版' }
]

// 添加编辑对话框的状态控制
const showEditDialog = ref(false)
const editServerForm = ref({
  id: null,
  server_name: '',
  ip_address: '',
  region: '上海',
  cpu: 2,
  memory: 2,
  storage: 40,
  category_id: '',
  bandwidth: 100,
  user_count: 0,
  total_traffic: 20
})

// 服务器分类映射
const categoryMap = {
  1: '4坑位版',
  2: '2坑位版'
}

// 排序相关
const sortField = ref('created_at')  // 默认按创建时间排序
const sortOrder = ref('desc')        // 默认降序

// 获取服务器列表
const fetchServers = async () => {
  try {
    console.log('开始获取服务器列表')
    const response = await api.getServers()
    console.log('获取服务器列表 - 原始响应:', response)

    if (response.success) {
      servers.value = response.servers.map(server => {
        // 从 category 字段获取分类名称，如果没有则使用 categoryMap 映射
        const categoryName = server.category || categoryMap[server.category_id] || '未知分类'
        console.log('处理服务器数据:', {
          服务器ID: server.id,
          分类名称: categoryName,
          原始category: server.category,
          原始category_id: server.category_id
        })

        return {
          ...server,
          category_id: server.category_id,  // 保持原始的 category_id
          category_name: categoryName
        }
      })
      console.log('最终处理后的服务器数据:', servers.value)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取服务器列表失败:', error)
    servers.value = []
  }
}

// 获取服务器分类
const fetchCategories = async () => {
  try {
    console.log('开始获取服务器分类')
    const response = await api.getServerCategories()
    console.log('服务器分类响应:', response)
    // 如果API返回为空，使用默认分类
    categories.value = Array.isArray(response) ? response : response.categories || defaultCategories
  } catch (error) {
    console.error('获取服务器分类失败:', error)
    categories.value = defaultCategories
  }
}

// 排序处理函数
const handleSort = (field) => {
  if (sortField.value === field) {
    // 如果点击的是当前排序字段，则切换排序顺序
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    // 如果点击的是新字段，则设置为该字段降序
    sortField.value = field
    sortOrder.value = 'desc'
  }
}

// 筛选后的服务器列表
const filteredServers = computed(() => {
  const filtered = servers.value.filter(server => {
    const matchesSearch = searchQuery.value === '' || 
      server.server_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      server.ip_address.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategoryId.value === 'all' || server.category_id === selectedCategoryId.value
    const matchesRegion = selectedRegion.value === 'all' || server.region === selectedRegion.value
    const matchesStatus = selectedStatus.value === 'all' || server.status === selectedStatus.value
    return matchesSearch && matchesCategory && matchesRegion && matchesStatus
  })
  
  // 排序
  return filtered.sort((a, b) => {
    const aValue = a[sortField.value]
    const bValue = b[sortField.value]
    if (sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
})

// 分页后的服务器列表
const paginatedServers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredServers.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredServers.value.length / itemsPerPage)
})

// 添加服务器
const addServer = async () => {
  try {
    // 检查所有必填字段
    if (!serverForm.value.server_name || !serverForm.value.ip_address || !serverForm.value.category_id ||
        !serverForm.value.region || !serverForm.value.cpu || !serverForm.value.memory || 
        !serverForm.value.storage) {
      alert('请填写所有必要信息（服务器名称、IP地址、分类、地区、CPU、内存、存储）')
      return
    }

    console.log('添加服务器 - 原始表单数据:', serverForm.value)

    const requestData = {
      ip_address: serverForm.value.ip_address,
      region: serverForm.value.region,
      cpu: serverForm.value.cpu,
      memory: serverForm.value.memory,
      category_id: Number(serverForm.value.category_id),  // 改回使用 category_id
      server_name: serverForm.value.server_name,
      storage: serverForm.value.storage,
      bandwidth: serverForm.value.bandwidth,
      user_count: serverForm.value.user_count,
      total_traffic: serverForm.value.total_traffic
    }

    console.log('添加服务器 - 发送的请求数据:', requestData)
    const response = await api.addServer(requestData)
    console.log('添加服务器 - 服务器响应:', response)

    if (response.success) {
      alert('添加服务器成功!')
      await fetchServers()
      // 重置表单
      serverForm.value = {
        server_name: '',
        ip_address: '',
        region: '上海',
        cpu: 2,
        memory: 2,
        storage: 40,
        category_id: '',
        bandwidth: 100,
        user_count: 0,
        total_traffic: 20
      }
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('添加服务器失败:', error)
  }
}

// 删除服务器
const deleteServer = async (serverId) => {
  if (confirm('确定要删除这台服务器吗？此操作将同时删除相关的容器数据!')) {
    try {
      const response = await api.deleteServer(serverId)
      if (response.success) {
        await fetchServers()
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      console.error('删除服务器失败:', error)
      alert('删除服务器失败: ' + error.message)
    }
  }
}

// 检查服务器状态
const checkServerStatus = async (serverId) => {
  try {
    const response = await api.getServerStatus(serverId)
    return response.success ? response.status : 'unknown'
  } catch (error) {
    console.error('获取服务器状态失败:', error)
    return 'unknown'
  }
}

// 健康检查
const checkServerHealth = async () => {
  try {
    const response = await api.getServerHealthCheck()
    if (response.success) {
      console.log('服务器健康状态:', response.health_check_results)
      alert('健康检查完成，请查看控制台日志')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    alert('服务器健康检查失败: ' + error.message)
  }
}

// 编辑服务器
const editServer = (server) => {
  console.log('编辑服务器被点击:', server)
  if (!server) {
    console.error('未获取到服务器数据')
    return
  }
  editServerForm.value = { 
    id: server.id,
    server_name: server.server_name,
    ip_address: server.ip_address,
    region: server.region,
    cpu: server.cpu,
    memory: server.memory,
    storage: server.storage,
    category_id: server.category_id,
    bandwidth: server.bandwidth,
    user_count: server.user_count,
    total_traffic: server.total_traffic
  }
  console.log('设置表单数据:', editServerForm.value)
  showEditDialog.value = true
  console.log('对话框显示状态:', showEditDialog.value)
}

// 更新服务器
const updateServer = async () => {
  try {
    console.log('更新服务器 - 原始表单数据:', editServerForm.value)
    
    const updateData = {
      ...editServerForm.value,
      category: Number(editServerForm.value.category_id)
    }
    console.log('更新服务器 - 处理后的数据:', updateData)

    const response = await api.updateServer(editServerForm.value.id, updateData)
    console.log('更新服务器 - 服务器响应:', response)

    if (response.success) {
      alert('更新服务器成功!')
      await fetchServers()  // 刷新列表
      showEditDialog.value = false  // 关闭对话框
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('更新服务器失败:', error)
    alert('更新服务器失败: ' + error.message)
  }
}

// 初始化加载
onMounted(async () => {
  console.log('ServerListView mounted')
  console.log('Layout component:', LayoutAuthenticated)
  try {
    await Promise.all([
      fetchServers(),
      fetchCategories()
    ])
  } catch (error) {
    console.error('初始化加载失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <!-- 添加调试信息 -->
      <div v-if="servers.length === 0" class="text-center py-4">
        <p>{{ '暂无服务器数据' }}</p>
      </div>
      
      <CardBox class="mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold flex items-center">
            <BaseIcon :path="mdiServer" class="mr-2" />
            服务器列表
          </h3>
          <div class="flex space-x-2">
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              @click="fetchServers"
              title="刷新列表"
            />
            <BaseButton
              :icon="mdiHeartPulse"
              color="success"
              @click="checkServerHealth"
              title="健康检查"
            />
          </div>
        </div>

        <!-- 筛选工具栏 -->
        <div class="flex flex-wrap gap-4 mb-4">
          <div class="flex-1 min-w-[200px]">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索服务器名称或IP..."
              class="w-full px-3 py-2 border rounded-md"
            >
          </div>
          <select
            v-model="selectedCategoryId"
            class="px-3 py-2 border rounded-md"
          >
            <option value="all">全部分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.category_name }}
            </option>
          </select>
          <select
            v-model="selectedRegion"
            class="px-3 py-2 border rounded-md"
          >
            <option value="all">全部地区</option>
            <option v-for="region in regions" :key="region" :value="region">
              {{ region }}
            </option>
          </select>
          <select
            v-model="selectedStatus"
            class="px-3 py-2 border rounded-md"
          >
            <option value="all">全部状态</option>
            <option value="running">运行中</option>
            <option value="stopped">已停止</option>
            <option value="restarting">重启中</option>
          </select>
        </div>

        <!-- 服务器列表表格 -->
        <div>
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700 table-fixed">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th @click="handleSort('server_name')" class="w-[10%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  服务器名称
                  <span v-if="sortField === 'server_name'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th class="w-[11%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">IP地址</th>
                <th class="w-[7%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">分类</th>
                <th class="w-[18%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">配置</th>
                <th class="w-[6%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">地区</th>
                <th class="w-[6%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">状态</th>
                <th class="w-[6%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">带宽</th>
                <th @click="handleSort('user_count')" class="w-[5%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  用户数
                  <span v-if="sortField === 'user_count'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th class="w-[6%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">流量</th>
                <th @click="handleSort('created_at')" class="w-[15%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  创建时间
                  <span v-if="sortField === 'created_at'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </th>
                <th class="w-[10%] px-2 py-3 text-center font-bold text-gray-700 dark:text-gray-300">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="server in paginatedServers" :key="server.id" 
                  class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200">
                <td class="px-2 py-2">
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    {{ server.server_name }}
                  </div>
                </td>
                <td class="px-2 py-2 font-mono text-sm">{{ server.ip_address }}</td>
                <td class="px-2 py-2">
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100">
                    {{ server.category_name }}
                  </span>
                </td>
                <td class="px-2 py-2 text-sm">
                  <div class="flex flex-col space-y-1">
                    <div class="flex items-center justify-center gap-1">
                      <span class="px-2 py-1 bg-gray-100 rounded-md dark:bg-gray-800">{{ server.cpu }}核</span>
                      <span class="px-2 py-1 bg-gray-100 rounded-md dark:bg-gray-800">{{ server.memory }}GB</span>
                    </div>
                    <div class="flex items-center justify-center">
                      <span class="px-2 py-1 bg-gray-100 rounded-md dark:bg-gray-800">{{ server.storage }}GB</span>
                    </div>
                  </div>
                </td>
                <td class="px-2 py-2 text-sm text-gray-600 dark:text-gray-400">{{ server.region }}</td>
                <td class="px-2 py-2">
                  <span class="px-2 py-1 rounded text-xs font-medium" :class="{
                    'bg-green-100 text-green-800': server.status === 'healthy',
                    'bg-red-100 text-red-800': server.status === 'unhealthy',
                    'bg-yellow-100 text-yellow-800': server.status === 'unknown'
                  }">
                    {{ server.status }}
                  </span>
                </td>
                <td class="px-2 py-2 text-sm">
                  <span class="font-medium">{{ server.bandwidth }}</span>
                  <span class="text-gray-500">M</span>
                </td>
                <td class="px-2 py-2 text-center font-medium">{{ server.user_count }}</td>
                <td class="px-2 py-2">
                  <span class="font-medium">{{ server.remaining_traffic }}</span>
                  <span class="text-sm text-gray-500">GB</span>
                </td>
                <td class="px-2 py-2 text-sm text-gray-600 dark:text-gray-400">
                  {{ new Date(server.created_at).toLocaleString() }}
                </td>
                <td class="px-2 py-2">
                  <div class="flex items-center space-x-2">
                    <BaseButton
                      :icon="mdiPencil"
                      color="info"
                      small
                      type="button"
                      @click="editServer(server)"
                      title="编辑"
                    />
                    <BaseButton
                      :icon="mdiDelete"
                      color="danger"
                      small
                      type="button"
                      @click="deleteServer(server.id)"
                      title="删除"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="mt-4 flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            显示 {{ (currentPage - 1) * itemsPerPage + 1 }} 到 
            {{ Math.min(currentPage * itemsPerPage, filteredServers.length) }} 条，
            共 {{ filteredServers.length }} 条
          </div>
          <div class="flex space-x-2">
            <BaseButton
              @click="currentPage--"
              :disabled="currentPage === 1"
              label="上一页"
            />
            <span class="px-4 py-2">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <BaseButton
              @click="currentPage++"
              :disabled="currentPage >= totalPages"
              label="下一页"
            />
          </div>
        </div>
      </CardBox>

      <!-- 添加服务器表单 -->
      <CardBox class="mb-6">
        <div class="flex items-center mb-6">
          <BaseIcon :path="mdiPlus" class="mr-2" />
          <h3 class="text-lg font-bold">添加服务器</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- 服务器名称 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              服务器名称 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="serverForm.server_name"
              type="text"
              required
              placeholder="请输入服务器名称"
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
          </div>

          <!-- IP地址 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              IP地址 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="serverForm.ip_address"
              type="text"
              required
              placeholder="请输入服务器IP地址"
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
          </div>

          <!-- 服务器分类 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              服务器分类 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="serverForm.category_id"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
              <option :value="1">4坑位版</option>
              <option :value="2">2坑位版</option>
            </select>
          </div>

          <!-- 地区选择 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              地区
            </label>
            <select
              v-model="serverForm.region"
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
              <option v-for="region in regions" :key="region" :value="region">
                {{ region }}
              </option>
            </select>
          </div>

          <!-- CPU配置 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              CPU核心数
            </label>
            <input
              v-model="serverForm.cpu"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
          </div>

          <!-- 内存配置 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              内存容量(GB)
            </label>
            <input
              v-model="serverForm.memory"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
          </div>

          <!-- 硬盘配置 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              硬盘容量(GB)
            </label>
            <input
              v-model="serverForm.storage"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
            >
          </div>

          <!-- 带宽配置 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              带宽(M)
            </label>
            <input
              v-model="serverForm.bandwidth"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
            >
          </div>

          <!-- 总流量配置 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              总流量(GB)
            </label>
            <input
              v-model="serverForm.total_traffic"
              type="number"
              min="1"
              required
              class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
            >
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <BaseButton
            :icon="mdiPlus"
            color="success"
            label="添加服务器"
            @click="addServer"
            class="w-full md:w-auto"
          />
        </div>
      </CardBox>

      <!-- 添加编辑对话框 -->
      <BaseDialog
        :show="showEditDialog"
        @close="showEditDialog = false"
        @confirm="updateServer"
      >
        <template #title>
          <div class="flex items-center">
            <BaseIcon :path="mdiPencil" class="mr-2" />
            编辑服务器
          </div>
        </template>
        
        <template #body>
          <div class="grid grid-cols-2 gap-4">
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">服务器名称</label>
              <input
                v-model="editServerForm.server_name"
                type="text"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">IP地址</label>
              <input
                v-model="editServerForm.ip_address"
                type="text"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <!-- 服务器分类 -->
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">服务器分类</label>
              <select
                v-model="editServerForm.category_id"
                class="w-full px-3 py-2 border rounded-md"
              >
                <option value="">请选择分类</option>
                <option v-for="category in categories" 
                        :key="category.id" 
                        :value="category.id"
                >
                  {{ category.category_name }}
                </option>
              </select>
            </div>
            
            <!-- 地区选择 -->
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">地区</label>
              <select
                v-model="editServerForm.region"
                class="w-full px-3 py-2 border rounded-md"
              >
                <option v-for="region in regions" 
                        :key="region" 
                        :value="region"
                >
                  {{ region }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">CPU核心数</label>
              <input
                v-model="editServerForm.cpu"
                type="number"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">内存(GB)</label>
              <input
                v-model="editServerForm.memory"
                type="number"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">硬盘(GB)</label>
              <input
                v-model="editServerForm.storage"
                type="number"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <!-- 带宽配置 -->
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">带宽(M)</label>
              <input
                v-model="editServerForm.bandwidth"
                type="number"
                min="1"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <!-- 用户数量 -->
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">用户数量</label>
              <input
                v-model="editServerForm.user_count"
                type="number"
                min="0"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <!-- 总流量配置 -->
            <div class="form-group">
              <label class="block text-sm font-medium mb-2">总流量(GB)</label>
              <input
                v-model="editServerForm.total_traffic"
                type="number"
                min="1"
                class="w-full px-3 py-2 border rounded-md"
              />
            </div>
          </div>
        </template>
        
        <template #footer>
          <div class="flex justify-end space-x-2">
            <BaseButton
              color="info"
              label="取消"
              @click="showEditDialog = false"
            />
            <BaseButton
              color="success"
              label="保存"
              @click="updateServer"
            />
          </div>
        </template>
      </BaseDialog>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}

/* 添加一些过渡效果 */
.cursor-pointer {
  transition: background-color 0.2s;
}

/* 确保表格内容居中对齐 */
td {
  text-align: center;
}

/* 让配置信息在单元格内居中 */
.flex.flex-col {
  align-items: center;
}
</style>
