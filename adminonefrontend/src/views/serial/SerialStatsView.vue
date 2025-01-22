<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton
        :icon="mdiChartBox"
        title="序列号统计"
        main
      >
        <BaseButton
          :icon="mdiRefresh"
          :loading="loading"
          @click="fetchStats"
          label="刷新"
          color="info"
        />
      </SectionTitleLineWithButton>

      <!-- 总体统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <CardBox>
          <div class="flex flex-col">
            <span class="text-gray-500">序列号总数</span>
            <span class="text-2xl font-bold">{{ totalSerials }}</span>
          </div>
        </CardBox>
        <CardBox>
          <div class="flex flex-col">
            <span class="text-gray-500">已使用序列号</span>
            <span class="text-2xl font-bold text-blue-600">{{ usedSerials }}</span>
          </div>
        </CardBox>
        <CardBox>
          <div class="flex flex-col">
            <span class="text-gray-500">未使用序列号</span>
            <span class="text-2xl font-bold text-green-600">{{ unusedSerials }}</span>
          </div>
        </CardBox>
        <CardBox>
          <div class="flex flex-col">
            <span class="text-gray-500">总销售额</span>
            <span class="text-2xl font-bold text-purple-600">¥{{ totalAmount }}</span>
          </div>
        </CardBox>
      </div>

      <!-- 图表区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 使用情况饼图 -->
        <CardBox>
          <div class="w-full h-80">
            <Pie
              v-if="usageChartData"
              :data="usageChartData"
              :options="usageChartOptions"
            />
          </div>
        </CardBox>

        <!-- 销售金额趋势图 -->
        <CardBox>
          <div class="w-full h-80">
            <Bar
              v-if="salesChartData"
              :data="salesChartData"
              :options="salesChartOptions"
            />
          </div>
        </CardBox>
      </div>

      <!-- 详细统计表格 -->
      <CardBox class="mt-6">
        <table class="w-full">
          <thead>
            <tr>
              <th class="text-left px-4 py-2">类型</th>
              <th class="text-right px-4 py-2">总数</th>
              <th class="text-right px-4 py-2">已用</th>
              <th class="text-right px-4 py-2">未用</th>
              <th class="text-right px-4 py-2">销售额</th>
              <th class="text-right px-4 py-2">潜在收入</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(stat, type) in typeStats" :key="type">
              <td class="px-4 py-2">{{ formatSerialType(type) }}</td>
              <td class="text-right px-4 py-2">{{ stat.total }}</td>
              <td class="text-right px-4 py-2">{{ stat.used }}</td>
              <td class="text-right px-4 py-2">{{ stat.unused }}</td>
              <td class="text-right px-4 py-2">¥{{ stat.revenue }}</td>
              <td class="text-right px-4 py-2">¥{{ stat.potential }}</td>
            </tr>
          </tbody>
        </table>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js'
import { Pie, Bar } from 'vue-chartjs'
import { mdiChartBox, mdiRefresh } from '@mdi/js'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title)

const loading = ref(false)
const serials = ref([])
const typeStats = ref({})

// 价格映射
const priceMap = {
  '030D05G': 5,   // 1个月基础型
  '030D10G': 10,  // 1个月加强型
  '180D05G': 25,  // 6个月基础型
  '180D10G': 50,  // 6个月加强型
  '360D05G': 50,  // 12个月基础型
  '360D10G': 100  // 12个月加强型
}

// 格式化序列号类型显示
const formatSerialType = (type) => {
  const durationMap = {
    '030': '1个月',
    '180': '6个月',
    '360': '12个月'
  }
  const trafficMap = {
    '05G': '基础型',
    '10G': '加强型'
  }
  
  // 从类型中提取时长和流量信息
  const duration = type.slice(0, 3)
  const traffic = type.slice(4, 7)
  
  // 获取对应的显示文本
  const durationText = durationMap[duration] || `${duration}天`
  const trafficText = trafficMap[traffic] || traffic
  
  // 返回格式化后的文本
  return `${durationText}-${trafficText}`
}

// 计算总计数据
const totalSerials = computed(() => serials.value.length)
const usedSerials = computed(() => serials.value.filter(s => s.status === 'used').length)
const unusedSerials = computed(() => serials.value.filter(s => s.status !== 'used').length)
const totalAmount = computed(() => {
  return serials.value.reduce((sum, serial) => {
    if (serial.status === 'used') {
      const price = priceMap[serial.serial_code.slice(0, 7)] || 0
      return sum + price
    }
    return sum
  }, 0)
})

// 使用情况饼图数据
const usageChartData = computed(() => ({
  labels: ['已使用', '未使用'],
  datasets: [{
    data: [usedSerials.value, unusedSerials.value],
    backgroundColor: ['#3B82F6', '#10B981']
  }]
}))

const usageChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    },
    title: {
      display: true,
      text: '序列号使用情况'
    }
  }
}

// 销售金额趋势图数据
const salesChartData = computed(() => {
  const monthlyData = getMonthlyStats()
  return {
    labels: monthlyData.map(d => d.month),
    datasets: [
      {
        label: '已售金额',
        data: monthlyData.map(d => d.revenue),
        backgroundColor: '#3B82F6'
      },
      {
        label: '潜在收入',
        data: monthlyData.map(d => d.potential),
        backgroundColor: '#10B981'
      }
    ]
  }
})

const salesChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    },
    title: {
      display: true,
      text: '销售金额统计'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: '金额 (元)'
      }
    }
  }
}

// 获取月度统计数据
const getMonthlyStats = () => {
  const months = {}
  const now = new Date()
  
  // 初始化最近6个月的数据
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    months[monthKey] = { revenue: 0, potential: 0 }
  }

  // 统计每个序列号
  serials.value.forEach(serial => {
    const price = priceMap[serial.serial_code.slice(0, 7)] || 0
    const createDate = new Date(serial.created_at)
    const monthKey = `${createDate.getFullYear()}-${String(createDate.getMonth() + 1).padStart(2, '0')}`
    
    if (months[monthKey]) {
      if (serial.status === 'used') {
        months[monthKey].revenue += price
      } else {
        months[monthKey].potential += price
      }
    }
  })

  return Object.entries(months).map(([month, data]) => ({
    month,
    ...data
  }))
}

// 获取统计数据
const fetchStats = async () => {
  try {
    loading.value = true
    const response = await api.getSerials()
    if (response.success) {
      serials.value = response.serial_numbers
      calculateTypeStats()
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算各类型序列号统计
const calculateTypeStats = () => {
  const stats = {}
  
  serials.value.forEach(serial => {
    // 修改这里：不要只取前7位，而是构造一个正确的类型标识
    const duration = serial.serial_code.slice(0, 3)
    const trafficType = serial.serial_code.slice(4, 7)
    const type = `${duration}-${trafficType === '05G' ? '基础型' : '加强型'}`
    
    if (!stats[type]) {
      stats[type] = {
        total: 0,
        used: 0,
        unused: 0,
        revenue: 0,
        potential: 0
      }
    }
    
    const price = priceMap[`${duration}D${trafficType}`] || 0
    
    stats[type].total++
    if (serial.status === 'used') {
      stats[type].used++
      stats[type].revenue += price
    } else {
      stats[type].unused++
      stats[type].potential += price
    }
  })
  
  typeStats.value = stats
}

// 添加一个辅助函数来格式化时长显示
const formatDuration = (duration) => {
  const durationMap = {
    '030': '1个月',
    '180': '6个月',
    '360': '12个月'
  }
  return durationMap[duration] || `${duration}天`
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.card-box-with-chart {
  @apply p-4;
}

table th {
  @apply bg-gray-50 dark:bg-gray-700;
}

table td, table th {
  @apply border-b dark:border-gray-700;
}

tr:hover td {
  @apply bg-gray-50 dark:bg-gray-800;
}
</style> 