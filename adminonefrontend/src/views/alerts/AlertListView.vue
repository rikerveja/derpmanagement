<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiBell } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const alerts = ref([])

onMounted(async () => {
  try {
    const response = await api.getAlerts()
    alerts.value = response
  } catch (error) {
    console.error('获取告警失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiBell" title="告警管理" main>
      </SectionTitleLineWithButton>

      <CardBox>
        <div v-if="alerts.length">
          {{ alerts }}
        </div>
        <div v-else>
          暂无告警信息
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 