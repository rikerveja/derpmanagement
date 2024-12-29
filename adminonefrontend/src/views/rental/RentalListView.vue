<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiClipboardList, mdiDownload, mdiTrashCan } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

const rentals = ref([])

const tableHeaders = [
  { text: '用户', value: 'username' },
  { text: '状态', value: 'rental_status' },
  { text: '到期时间', value: 'rental_expiry' },
  { text: '操作', value: 'actions' }
]

onMounted(async () => {
  try {
    const response = await api.getRentalHistory()
    rentals.value = response
  } catch (error) {
    console.error('获取租赁历史失败:', error)
  }
})

const downloadHistory = async (rental) => {
  try {
    await api.downloadRentalHistory(rental.id)
  } catch (error) {
    console.error('下载租赁历史失败:', error)
  }
}

const deleteHistory = async (rental) => {
  try {
    await api.deleteRentalHistory(rental.id)
    const response = await api.getRentalHistory()
    rentals.value = response
  } catch (error) {
    console.error('删除租赁历史失败:', error)
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiClipboardList" title="租赁管理" main>
      </SectionTitleLineWithButton>

      <CardBox has-table>
        <BaseTable
          :headers="tableHeaders"
          :items="rentals"
          :hide-bottom-border="false"
        >
          <template #item-rental_status="{ item }">
            <small :class="{
              'text-green-500': item.rental_status === 'active',
              'text-red-500': item.rental_status === 'expired'
            }">
              {{ item.rental_status }}
            </small>
          </template>
          <template #item-actions="{ item }">
            <BaseButtons type="justify-start lg:justify-end" no-wrap>
              <BaseButton
                color="info"
                :icon="mdiDownload"
                small
                @click="downloadHistory(item)"
              />
              <BaseButton
                color="danger"
                :icon="mdiTrashCan"
                small
                @click="deleteHistory(item)"
              />
            </BaseButtons>
          </template>
        </BaseTable>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 