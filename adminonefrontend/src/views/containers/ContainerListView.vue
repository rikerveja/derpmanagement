<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiDocker } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const containers = ref([])

onMounted(async () => {
  try {
    const response = await api.getContainers()
    containers.value = response.containers
  } catch (error) {
    console.error('获取容器列表失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiDocker" title="容器列表" main>
      </SectionTitleLineWithButton>

      <CardBox>
        <!-- TODO: 添加容器列表表格 -->
        <div v-if="containers.length">
          {{ containers }}
        </div>
        <div v-else>
          暂无容器数据
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 