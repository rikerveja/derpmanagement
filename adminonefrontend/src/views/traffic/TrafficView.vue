<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiChartLine } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const trafficData = ref(null)

onMounted(async () => {
  try {
    const response = await api.getRealTimeTraffic()
    trafficData.value = response
  } catch (error) {
    console.error('获取流量数据失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiChartLine" title="流量监控" main>
      </SectionTitleLineWithButton>

      <CardBox>
        <!-- TODO: 添加流量图表 -->
        <div v-if="trafficData">
          {{ trafficData }}
        </div>
        <div v-else>
          加载中...
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 