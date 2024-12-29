<script setup>
import { ref, onMounted } from 'vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiServerNetwork } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const haStatus = ref(null)

onMounted(async () => {
  try {
    const response = await api.getHaHealth()
    haStatus.value = response
  } catch (error) {
    console.error('获取高可用状态失败:', error)
  }
})
</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiServerNetwork" title="高可用配置" main>
    </SectionTitleLineWithButton>

    <CardBox>
      <div v-if="haStatus">
        {{ haStatus }}
      </div>
      <div v-else>
        加载中...
      </div>
    </CardBox>
  </SectionMain>
</template> 