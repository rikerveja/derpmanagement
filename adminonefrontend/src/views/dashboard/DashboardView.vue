<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiChartTimelineVariant, mdiAccountMultiple, mdiDocker, mdiChartLine, mdiEye } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'
import BaseIcon from '@/components/BaseIcon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseLevel from '@/components/BaseLevel.vue'

const containers = ref([])
const traffic = ref(null)
const alerts = ref([])
const rentalInfo = ref(null)

onMounted(async () => {
  try {
    // 获取容器列表
    const containersData = await api.getContainers()
    containers.value = containersData.containers

    // 获取实时流量
    const trafficData = await api.getRealTimeTraffic()
    traffic.value = trafficData.traffic

    // 获取告警信息
    const alertsData = await api.getAlerts()
    alerts.value = alertsData.alerts

    // 获取租赁信息
    const rentalData = await api.getRentalInfo()
    rentalInfo.value = rentalData
  } catch (error) {
    console.error('获取数据失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="系统概览" main>
      </SectionTitleLineWithButton>

      <!-- 状态卡片 -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3 mb-6">
        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-blue-500 p-3">
                <BaseIcon :path="mdiDocker" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">容器总数</p>
              <p class="text-lg font-semibold">{{ containers.length }}</p>
            </div>
          </div>
        </CardBox>

        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-green-500 p-3">
                <BaseIcon :path="mdiChartLine" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">当前流量</p>
              <p class="text-lg font-semibold">{{ traffic?.in || 0 }} MB/s</p>
            </div>
          </div>
        </CardBox>

        <CardBox>
          <div class="flex items-center">
            <div class="flex-shrink-0 p-4">
              <div class="rounded-full bg-red-500 p-3">
                <BaseIcon :path="mdiAccountMultiple" class="text-white" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600">告警数量</p>
              <p class="text-lg font-semibold">{{ alerts.length }}</p>
            </div>
          </div>
        </CardBox>
      </div>

      <!-- 租赁信息 -->
      <CardBox class="mb-6">
        <div v-if="rentalInfo">
          <BaseLevel class="mb-4">
            <h3 class="text-lg font-medium">租赁信息</h3>
          </BaseLevel>
          <div class="space-y-2">
            <p>状态: {{ rentalInfo.rental_status }}</p>
            <p>到期时间: {{ rentalInfo.rental_expiry }}</p>
          </div>
        </div>
      </CardBox>

      <!-- 最近告警 -->
      <CardBox>
        <BaseLevel class="mb-4">
          <h3 class="text-lg font-medium">最近告警</h3>
          <BaseButton 
            v-if="alerts.length"
            :icon="mdiEye" 
            to="/alerts" 
            color="info" 
            outline 
            label="查看全部" 
          />
        </BaseLevel>
        <div v-if="alerts.length" class="space-y-4">
          <div v-for="alert in alerts.slice(0, 5)" :key="alert.alert_id" class="p-4 border-b">
            <p class="font-medium">{{ alert.message }}</p>
            <p class="text-sm text-gray-500">{{ alert.timestamp }}</p>
          </div>
        </div>
        <div v-else>
          暂无告警信息
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 