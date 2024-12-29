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
import { mdiDocker } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const router = useRouter()
const form = ref({
  name: '',
  image: '',
  port: ''
})

const submit = async () => {
  try {
    await api.createContainer(form.value)
    router.push('/containers')
  } catch (error) {
    console.error('创建容器失败:', error)
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiDocker" title="新建容器" main>
      </SectionTitleLineWithButton>

      <CardBox is-form @submit.prevent="submit">
        <FormField label="容器名称">
          <FormControl v-model="form.name" />
        </FormField>

        <FormField label="镜像">
          <FormControl v-model="form.image" />
        </FormField>

        <FormField label="端口">
          <FormControl v-model="form.port" type="number" />
        </FormField>

        <template #footer>
          <BaseButtons>
            <BaseButton type="submit" color="info" label="创建" />
            <BaseButton to="/containers" color="info" outline label="取消" />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 