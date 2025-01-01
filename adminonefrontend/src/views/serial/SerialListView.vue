<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiKey, mdiDownload, mdiTrashCan, mdiPlus } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

const serials = ref([])

const tableHeaders = [
  { text: '序列号', value: 'serial_code' },
  { text: '状态', value: 'status' },
  { text: '发放给', value: 'issued_to' },
  { text: '到期时间', value: 'expiry_date' },
  { text: '操作', value: 'actions' }
]

const generateSerial = async () => {
  try {
    const response = await api.generateSerial({
      type: 'rental',
      expiry_date: new Date().toISOString()
    })
    // 刷新列表
    fetchSerials()
  } catch (error) {
    console.error('生成序列号失败:', error)
  }
}

const fetchSerials = async () => {
  try {
    // 这里需要添加获取序列号列表的API
    const response = await api.getSerialList()
    serials.value = response
  } catch (error) {
    console.error('获取序列号列表失败:', error)
  }
}

const downloadSerial = async (serial) => {
  try {
    await api.downloadSerial(serial.serial_code)
  } catch (error) {
    console.error('下载序列号失败:', error)
  }
}

const deleteSerial = async (serial) => {
  try {
    await api.deleteSerial(serial.serial_code)
    await fetchSerials()
  } catch (error) {
    console.error('删除序列号失败:', error)
  }
}

onMounted(fetchSerials)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiKey" title="序列号管理" main>
        <BaseButton 
          :icon="mdiPlus"
          label="生成序列号" 
          color="info" 
          @click="generateSerial" 
        />
      </SectionTitleLineWithButton>

      <CardBox has-table>
        <BaseTable
          :headers="tableHeaders"
          :items="serials"
          :hide-bottom-border="false"
        >
          <template #item-actions="{ item }">
            <BaseButtons type="justify-start lg:justify-end" no-wrap>
              <BaseButton
                color="info"
                :icon="mdiDownload"
                small
                @click="downloadSerial(item)"
              />
              <BaseButton
                color="danger"
                :icon="mdiTrashCan"
                small
                @click="deleteSerial(item)"
              />
            </BaseButtons>
          </template>
        </BaseTable>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 