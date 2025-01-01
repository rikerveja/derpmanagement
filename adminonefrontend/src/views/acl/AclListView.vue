<script setup>
import { ref, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { mdiShieldAccount, mdiDownload, mdiTrashCan, mdiPlus } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseTable from '@/components/BaseTable.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

const acls = ref([])

const tableHeaders = [
  { text: '用户', value: 'username' },
  { text: '权限', value: 'permissions' },
  { text: '创建时间', value: 'created_at' },
  { text: '操作', value: 'actions' }
]

const downloadAcl = async (acl) => {
  try {
    await api.downloadAcl(acl.id)
  } catch (error) {
    console.error('下载ACL失败:', error)
  }
}

const deleteAcl = async (acl) => {
  try {
    await api.deleteAcl(acl.id)
    // 重新获取列表
    const response = await api.getAclLogs()
    acls.value = response
  } catch (error) {
    console.error('删除ACL失败:', error)
  }
}

onMounted(async () => {
  try {
    // 获取ACL列表
    const response = await api.getAclLogs()
    acls.value = response
  } catch (error) {
    console.error('获取ACL列表失败:', error)
  }
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiShieldAccount" title="ACL管理" main>
        <BaseButton 
          :icon="mdiPlus"
          to="/acl/generate" 
          color="info" 
          label="生成ACL" 
        />
      </SectionTitleLineWithButton>

      <CardBox has-table>
        <BaseTable
          :headers="tableHeaders"
          :items="acls"
          :hide-bottom-border="false"
        >
          <template #item-permissions="{ item }">
            <small class="text-gray-500">
              {{ item.permissions.join(', ') }}
            </small>
          </template>
          <template #item-actions="{ item }">
            <BaseButtons type="justify-start lg:justify-end" no-wrap>
              <BaseButton
                color="info"
                :icon="mdiDownload"
                small
                @click="downloadAcl(item)"
              />
              <BaseButton
                color="danger"
                :icon="mdiTrashCan"
                small
                @click="deleteAcl(item)"
              />
            </BaseButtons>
          </template>
        </BaseTable>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 