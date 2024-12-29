<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import TableSampleClients from '@/components/TableSampleClients.vue'
import { mdiAccountMultiple } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'

const users = ref([])

onMounted(async () => {
  // TODO: 从API获取用户列表
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccountMultiple" title="用户管理" main>
      </SectionTitleLineWithButton>

      <CardBox has-table>
        <TableSampleClients />
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 