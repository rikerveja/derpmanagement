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
const selectedCategory = ref('all')
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

// 获取服务器列表
const fetchServers = async () => {
  try {
    console.log('开始获取服务器列表')
    const response = await api.getServers()
    console.log('服务器列表响应:', response)
    if (response.success) {
      servers.value = response.servers || []
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

// 筛选后的服务器列表
const filteredServers = computed(() => {
  return servers.value.filter(server => {
    const matchesSearch = searchQuery.value === '' || 
      server.server_name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      server.ip.includes(searchQuery.value)
    const matchesCategory = selectedCategory.value === 'all' || server.category_id === selectedCategory.value
    const matchesRegion = selectedRegion.value === 'all' || server.region === selectedRegion.value
    const matchesStatus = selectedStatus.value === 'all' || server.status === selectedStatus.value
    return matchesSearch && matchesCategory && matchesRegion && matchesStatus
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

    // 打印表单数据
    console.log('表单数据:', serverForm.value) // 确保数据完整

    // 封装请求数据
    const requestData = {
      ip_address: serverForm.value.ip_address,
      region: serverForm.value.region,
      cpu: serverForm.value.cpu,
      memory: serverForm.value.memory,
      category_id: serverForm.value.category_id,
      server_name: serverForm.value.server_name,
      storage: serverForm.value.storage,
      bandwidth: serverForm.value.bandwidth,
      user_count: serverForm.value.user_count,
      total_traffic: serverForm.value.total_traffic
    }

    // 打印请求数据
    console.log('准备发送的请求数据:', JSON.stringify(requestData, null, 2))

    const response = await api.addServer(requestData)
    console.log('服务器响应:', response)

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
    console.error('添加服务器失败，完整错误信息:', error)
    console.error('错误响应数据:', error.response?.data)
    console.error('错误状态码:', error.response?.status)
    alert('添加服务器失败: ' + (error.response?.data?.message || error.message))
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
  console.log('编辑服务器:', server)
  // TODO: 实现编辑服务器功能
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
            v-model="selectedCategory"
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
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left">服务器名称</th>
                <th class="px-4 py-3 text-left">IP地址</th>
                <th class="px-4 py-3 text-left">分类</th>
                <th class="px-4 py-3 text-left">配置</th>
                <th class="px-4 py-3 text-left">地区</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">带宽</th>
                <th class="px-4 py-3 text-left">用户数</th>
                <th class="px-4 py-3 text-left">剩余流量</th>
                <th class="px-4 py-3 text-left">创建时间</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="server in paginatedServers" :key="server.id" 
                  class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3">{{ server.server_name }}</td>
                <td class="px-4 py-3">{{ server.ip_address }}</td>
                <td class="px-4 py-3">
                  {{ categories.find(c => c.id === server.category_id)?.category_name }}
                </td>
                <td class="px-4 py-3">
                  {{ server.cpu }}核 / {{ server.memory }}GB / {{ server.storage }}GB
                </td>
                <td class="px-4 py-3">{{ server.region }}</td>
                <td class="px-4 py-3">
                  <span :class="{
                    'px-2 py-1 rounded text-xs font-medium': true,
                    'bg-green-100 text-green-800': server.status === 'running',
                    'bg-red-100 text-red-800': server.status === 'stopped',
                    'bg-yellow-100 text-yellow-800': server.status === 'restarting'
                  }">
                    {{ 
                      server.status === 'running' ? '运行中' :
                      server.status === 'stopped' ? '已停止' :
                      server.status === 'restarting' ? '重启中' : '未知'
                    }}
                  </span>
                </td>
                <td class="px-4 py-3">{{ server.bandwidth }}M</td>
                <td class="px-4 py-3">{{ server.user_count }}</td>
                <td class="px-4 py-3">{{ server.remaining_traffic }}GB</td>
                <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {{ new Date(server.created_at).toLocaleString() }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex space-x-2">
                    <BaseButton
                      :icon="mdiPencil"
                      color="info"
                      small
                      @click="editServer(server)"
                    />
                    <BaseButton
                      :icon="mdiDelete"
                      color="danger"
                      small
                      @click="deleteServer(server.id)"
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
              <option value="">请选择分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.category_name }}
              </option>
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

          <!-- 显示配置和带宽 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              配置和带宽
            </label>
            <p class="text-gray-700 dark:text-gray-300">
              {{ serverForm.cpu }} 核 / {{ serverForm.memory }} GB / {{ serverForm.storage }} GB / 带宽: {{ serverForm.bandwidth }} M
            </p>
          </div>

          <!-- 服务器类型 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              服务器类型
            </label>
            <input
              v-model="serverForm.server_type"
              type="text"
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
</style>

