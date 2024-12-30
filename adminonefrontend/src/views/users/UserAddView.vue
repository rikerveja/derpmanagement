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
import { mdiAccountPlus } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const router = useRouter()
const form = ref({
  username: '',
  password: '',
  email: '',
  role: '普通用户' // 默认角色
})

const submit = async () => {
  try {
    await api.addUser(form.value)
    router.push('/users')
  } catch (error) {
    console.error('添加用户失败:', error)
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccountPlus" title="添加用户" main>
      </SectionTitleLineWithButton>

      <CardBox is-form @submit.prevent="submit">
        <FormField label="用户名">
          <FormControl v-model="form.username" />
        </FormField>

        <FormField label="密码">
          <FormControl v-model="form.password" type="password" />
        </FormField>

        <FormField label="邮箱">
          <FormControl v-model="form.email" type="email" />
        </FormField>

        <FormField label="角色">
          <select v-model="form.role">
            <option value="普通用户">普通用户</option>
            <option value="分销员">分销员</option>
          </select>
        </FormField>

        <template #footer>
          <BaseButtons>
            <BaseButton type="submit" color="info" label="添加" />
            <BaseButton to="/users" color="info" outline label="取消" />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
/* 样式可以根据需要进行调整 */
</style> 
