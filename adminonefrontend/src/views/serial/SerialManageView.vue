<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiKey, 
  mdiPlus, 
  mdiDelete, 
  mdiRefresh,
  mdiExport,
  mdiMagnify,
  mdiFilter,
  mdiCheckboxMultipleMarked
} from '@mdi/js'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

// 序列号列表数据
const serials = ref([])
const currentPage = ref(1)
const itemsPerPage = 10
const searchQuery = ref('')
const selectedStatus = ref('all')
const selectedTimeType = ref('all')
const selectedTrafficType = ref('all')
const selectedSerials = ref([])

// 修改筛选选项的定义
const timeTypeOptions = [
  { value: 'all', label: '全部时长' },
  { value: 'monthly', label: '月付版(30天)' },
  { value: 'half_year', label: '半年版(180天)' },
  { value: 'yearly', label: '年付版(360天)' }
]

// 修改流量类型选项的计算属性
const availableTrafficTypeOptions = computed(() => {
  return [
    { value: 'all', label: '全部流量' },
    { value: 'basic', label: '基础型(5G/月)' },
    { value: 'premium', label: '加强型(10G/月)' }
  ]
})

// 筛选和搜索后的序列号
const filteredSerials = computed(() => {
  return serials.value.filter(serial => {
    const matchesSearch = (serial.serial_code || '').toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         (serial.remarks || '').toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = selectedStatus.value === 'all' || serial.status === selectedStatus.value
    // 从序列号代码中提取时间和流量类型
    const timeType = (serial.serial_code || '').includes('030D') ? 'monthly' : 
                     (serial.serial_code || '').includes('180D') ? 'half_year' : 'yearly'
    const trafficType = (serial.serial_code || '').includes('05G') ? 'basic' : 'premium'
    const matchesTimeType = selectedTimeType.value === 'all' || timeType === selectedTimeType.value
    const matchesTrafficType = selectedTrafficType.value === 'all' || trafficType === selectedTrafficType.value
    return matchesSearch && matchesStatus && matchesTimeType && matchesTrafficType
  })
})

// 分页后的序列号
const paginatedSerials = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredSerials.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredSerials.value.length / itemsPerPage)
})

// 批量操作
const handleBatchDelete = async () => {
  if (confirm(`确定要删除选中的 ${selectedSerials.value.length} 个序列号吗？`)) {
    try {
      await api.batchDeleteSerials(selectedSerials.value)
      await fetchSerials()
      selectedSerials.value = []
    } catch (error) {
      console.error('批量删除失败:', error)
      alert('批量删除失败: ' + error.message)
    }
  }
}

// 导出序列号
const exportSerials = async () => {
  try {
    const data = selectedSerials.value.length > 0 
      ? selectedSerials.value.map(id => serials.value.find(s => s.id === id))
      : filteredSerials.value

    // 构造CSV数据
    const csvContent = [
      ['序列号代码', '创建时间', '过期时间', '有效期(天)', '状态'].join(','),
      ...data.map(serial => [
        serial.serial_code,
        new Date(serial.created_at).toLocaleString(),
        new Date(serial.expires_at).toLocaleString(),
        serial.valid_days,
        serial.expired ? '已过期' : (serial.status === 'unused' ? '未使用' : '已使用')
      ].join(','))
    ].join('\n')

    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `序列号列表_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 修改时间类型定义
const timeTypes = [
  { value: 'monthly', label: '月付版', days: 30 },
  { value: 'half_year', label: '半年版', days: 180 },
  { value: 'yearly', label: '年付版', days: 360 }
]

// 修改流量类型定义
const trafficTypes = [
  { value: 'basic', label: '基础型(5G/月)', traffic: 5 },
  { value: 'premium', label: '加强型(10G/月)', traffic: 10 }
]

// 简化计算属性：根据时间类型筛选可用的流量类型
const availableTrafficTypes = computed(() => {
  if (serialForm.value.timeType === 'trial') {
    return [{ value: 'trial', label: '试用流量(1G)', traffic: 1 }]
  }
  return trafficTypes
})

// 修改表单数据结构
const serialForm = ref({
  timeType: 'monthly',
  trafficType: 'basic',
  count: 1,
  prefix: '',
  validDays: 30,
})

// 监听时间类型变化
watch(() => serialForm.value.timeType, (newType) => {
  if (newType === 'trial') {
    serialForm.value.trafficType = 'trial'
  } else if (serialForm.value.trafficType === 'trial') {
    serialForm.value.trafficType = 'basic'
  }
})

// 修改生成序列号的方法
const generateSerials = async () => {
  try {
    // 输入验证
    if (serialForm.value.count > 30) {
      alert('一次最多只能生成30个序列号')
      return
    }
    if (serialForm.value.validDays > 100) {
      alert('序列号有效期最长为100天')
      return
    }
    if (serialForm.value.prefix && serialForm.value.prefix.length > 10) {
      alert('前缀最长为10个字符')
      return
    }

    // 构造前缀
    const prefix = `${serialForm.value.prefix || ''}${serialForm.value.timeType === 'monthly' ? '030D' : serialForm.value.timeType === 'half_year' ? '180D' : '360D'}${serialForm.value.trafficType === 'basic' ? '05G' : '10G'}`
    
    // 构造请求数据
    const requestData = {
      "count": parseInt(serialForm.value.count),
      "valid_days": parseInt(serialForm.value.validDays),
      "prefix": prefix
    }

    const response = await api.generateSerials(requestData)
    if (response.success && response.serial_numbers) {
      alert('序列号生成成功!')
      await fetchSerials()
    } else {
      throw new Error('生成序列号失败')
    }
    
    // 重置表单
    serialForm.value = {
      timeType: 'monthly',
      trafficType: 'basic',
      count: 1,
      prefix: '',
      validDays: 30,
    }
  } catch (error) {
    console.error('生成序列号失败:', error)
    alert('生成序列号失败: ' + error.message)
  }
}

// 获取序列号列表
const fetchSerials = async () => {
  try {
    console.log('开始获取序列号列表')
    const response = await api.getSerials()
    console.log('获取到的数据:', response)
    if (response && response.serial_numbers) {
      serials.value = response.serial_numbers
    } else {
      console.error('返回数据格式不正确:', response)
      serials.value = []
    }
  } catch (error) {
    console.error('获取序列号列表失败:', error)
    serials.value = []
  }
}

// 删除序列号
const deleteSerial = async (serialCode) => {
  try {
    if (!confirm('确定要删除这个序列号吗？')) return
    await api.deleteSerial(serialCode)
    await fetchSerials()
    selectedSerials.value = []
  } catch (error) {
    console.error('删除序列号失败:', error)
    alert('删除序列号失败: ' + error.message)
  }
}

// 确保在组件挂载时获取数据
onMounted(() => {
  console.log('组件已挂载，开始获取数据')
  fetchSerials()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <!-- 序列号列表 -->
      <CardBox class="mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold flex items-center">
            <BaseIcon :path="mdiKey" class="mr-2" />
            序列号列表
          </h3>
          <div class="flex space-x-2">
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              @click="fetchSerials"
              title="刷新列表"
            />
            <BaseButton
              :icon="mdiExport"
              color="success"
              @click="exportSerials"
              title="导出序列号"
            />
          </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="mb-4 flex flex-wrap gap-4">
          <div class="flex-1 min-w-[200px]">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索序列号或备注"
                class="w-full pl-10 pr-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
              >
              <BaseIcon
                :path="mdiMagnify"
                class="absolute left-3 top-2.5 text-gray-400 dark:text-gray-500"
                size="20"
              />
            </div>
          </div>
          
          <select
            v-model="selectedStatus"
            class="px-4 py-2 pr-6 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
          >
            <option value="all">全部状态</option>
            <option value="unused">未使用</option>
            <option value="used">已使用</option>
            <option value="expired">已过期</option>
          </select>

          <select
            v-model="selectedTimeType"
            class="px-4 py-2 pr-6 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
          >
            <option v-for="type in timeTypeOptions" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>

          <select
            v-model="selectedTrafficType"
            class="px-4 py-2 pr-6 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
          >
            <option v-for="type in availableTrafficTypeOptions" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>

          <!-- 批量操作按钮 -->
          <BaseButton
            v-if="selectedSerials.length > 0"
            :icon="mdiDelete"
            color="danger"
            @click="handleBatchDelete"
            :label="`删除选中(${selectedSerials.length})`"
          />
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3">
                  <input type="checkbox" @change="e => 
                    selectedSerials = e.target.checked 
                      ? paginatedSerials.map(s => s.serial_code)
                      : []"
                  >
                </th>
                <th>序列号代码</th>
                <th>创建时间</th>
                <th>过期时间</th>
                <th>有效期(天)</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="serial in paginatedSerials" :key="serial.serial_code" 
                  class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3">
                  <input
                    type="checkbox"
                    v-model="selectedSerials"
                    :value="serial.serial_code"
                    class="rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700"
                  >
                </td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-300">{{ serial.serial_code }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-300">{{ new Date(serial.created_at).toLocaleString() }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-300">{{ new Date(serial.expires_at).toLocaleString() }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-300">{{ serial.valid_days }}</td>
                <td class="px-4 py-3 text-sm">
                  <span :class="{
                    'px-2 py-1 rounded text-xs font-medium': true,
                    'bg-green-100 text-green-800': serial.status === 'unused',
                    'bg-red-100 text-red-800': serial.status === 'used',
                    'bg-gray-100 text-gray-800': serial.expired
                  }">
                    {{ serial.expired ? '已过期' : (serial.status === 'unused' ? '未使用' : '已使用') }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm">
                  <BaseButton
                    v-if="serial.status === 'unused'"
                    :icon="mdiDelete"
                    color="danger"
                    small
                    @click="deleteSerial(serial.serial_code)"
                    title="删除"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="mt-4 flex items-center justify-between">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            显示 {{ (currentPage - 1) * itemsPerPage + 1 }} 到 
            {{ Math.min(currentPage * itemsPerPage, filteredSerials.length) }} 条，
            共 {{ filteredSerials.length }} 条
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

      <!-- 生成序列号表单 -->
      <CardBox>
        <div class="flex items-center mb-4">
          <BaseIcon :path="mdiPlus" class="mr-2" />
          <h3 class="text-lg font-bold">生成序列号</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">时间类型</label>
            <select
              v-model="serialForm.timeType"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option v-for="type in timeTypes" :key="type.value" :value="type.value">
                {{ type.label }}{{ type.days > 0 ? ` (${type.days}天)` : '' }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">流量类型</label>
            <select
              v-model="serialForm.trafficType"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              :disabled="serialForm.timeType === 'trial'"
            >
              <option v-for="type in availableTrafficTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">序列号有效期(天)</label>
            <input
              v-model="serialForm.validDays"
              type="number"
              min="1"
              max="100"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
          </div>

          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">生成数量</label>
            <input
              v-model="serialForm.count"
              type="number"
              min="1"
              max="30"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
          </div>

          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">前缀(可选)</label>
            <input
              v-model="serialForm.prefix"
              type="text"
              maxlength="10"
              class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
          </div>
        </div>

        <!-- 显示当前选择的配置信息 -->
        <div class="mt-4 text-sm text-gray-600 dark:text-gray-400">
          当前配置：
          <span>
            {{ timeTypes.find(t => t.value === serialForm.timeType)?.label }} + 
            {{ trafficTypes.find(t => t.value === serialForm.trafficType)?.label }}
          </span>
          <span class="ml-2">
            (序列号有效期: {{ serialForm.validDays }}天)
          </span>
        </div>

        <!-- 修改流量说明 -->
        <div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          选择的套餐将在到期时自动失效，请在到期前及时续费
        </div>

        <div class="mt-6">
          <BaseButton
            :icon="mdiPlus"
            color="success"
            label="生成序列号"
            @click="generateSerials"
          />
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-group {
  margin-bottom: 1rem;
}

/* 添加一些过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 
