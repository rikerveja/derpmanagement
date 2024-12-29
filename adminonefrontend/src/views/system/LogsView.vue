<script setup>
import { ref, onMounted } from 'vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiTextBox } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const logs = ref([])

onMounted(async () => {
  try {
    const response = await api.getSystemLogs()
    logs.value = response
  } catch (error) {
    console.error('获取系统日志失败:', error)
  }
})
</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiTextBox" title="系统日志" main>
    </SectionTitleLineWithButton>

    <CardBox>
      <div v-if="logs.length">
        {{ logs }}
      </div>
      <div v-else>
        暂无日志数据
      </div>
    </CardBox>
  </SectionMain>
</template> 