<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import FormCheckRadioGroup from '@/components/FormCheckRadioGroup.vue'
import { mdiShieldAccount } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const router = useRouter()
const form = ref({
  username: '',
  permissions: []
})

const permissionOptions = [
  { label: '读取', value: 'read' },
  { label: '写入', value: 'write' },
  { label: '执行', value: 'execute' },
  { label: '管理', value: 'admin' }
]

const submit = async () => {
  try {
    await api.generateAcl(form.value.username, form.value.permissions)
    router.push('/acl')
  } catch (error) {
    console.error('生成ACL失败:', error)
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiShieldAccount" title="生成ACL" main>
      </SectionTitleLineWithButton>

      <CardBox is-form @submit.prevent="submit">
        <FormField label="用户名" help="选择要生成ACL的用户">
          <FormControl v-model="form.username" />
        </FormField>

        <FormField label="权限" help="选择要授予的权限">
          <FormCheckRadioGroup
            v-model="form.permissions"
            name="permissions"
            :options="permissionOptions"
            type="checkbox"
          />
        </FormField>

        <template #footer>
          <BaseButtons>
            <BaseButton type="submit" color="info" label="生成" />
            <BaseButton to="/acl" color="info" outline label="取消" />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 