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
import { mdiAccountPlus, mdiEmailOutline } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const verificationSent = ref(false)
const countdown = ref(0)

const form = ref({
  username: '',
  password: '',
  email: '',
  verification_code: '',
  role: '普通用户'
})

// 表单验证
const validateForm = () => {
  if (!form.value.username) return '请输入用户名'
  if (!form.value.password) return '请输入密码'
  if (!form.value.email) return '请输入邮箱'
  if (!form.value.verification_code) return '请输入验证码'
  return ''
}

// 发送验证码
const sendVerificationCode = async () => {
  if (!form.value.email) {
    error.value = '请先输入邮箱'
    return
  }

  try {
    loading.value = true
    const response = await api.sendVerificationCode(form.value.email)
    if (response.success) {
      verificationSent.value = true
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
          verificationSent.value = false
        }
      }, 1000)
    } else {
      error.value = response.message || '发送验证码失败'
    }
  } catch (err) {
    error.value = '发送验证码失败: ' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

// 提交表单
const submit = async () => {
  error.value = validateForm()
  if (error.value) return

  try {
    loading.value = true
    const response = await api.addUser(form.value)
    if (response.success) {
      router.push('/users')
    } else {
      error.value = response.message || '添加用户失败'
    }
  } catch (err) {
    console.error('添加用户失败:', err)
    error.value = err.message || '添加用户失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiAccountPlus" title="添加用户" main>
      </SectionTitleLineWithButton>

      <CardBox is-form @submit.prevent="submit">
        <!-- 错误提示 -->
        <div v-if="error" class="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
          {{ error }}
        </div>

        <FormField label="用户名">
          <FormControl 
            v-model="form.username" 
            :disabled="loading"
            placeholder="请输入用户名"
          />
        </FormField>

        <FormField label="密码">
          <FormControl 
            v-model="form.password" 
            type="password" 
            :disabled="loading"
            placeholder="请输入密码"
          />
        </FormField>

        <FormField label="邮箱">
          <div class="flex space-x-2">
            <FormControl 
              v-model="form.email" 
              type="email" 
              :disabled="loading"
              placeholder="请输入邮箱"
              class="flex-1"
            />
            <BaseButton
              :icon="mdiEmailOutline"
              :label="verificationSent ? `${countdown}s` : '发送验证码'"
              :disabled="loading || verificationSent || !form.email"
              @click="sendVerificationCode"
              color="info"
            />
          </div>
        </FormField>

        <FormField label="验证码">
          <FormControl 
            v-model="form.verification_code"
            :disabled="loading"
            placeholder="请输入验证码"
          />
        </FormField>

        <FormField label="角色">
          <select 
            v-model="form.role"
            class="form-select w-full rounded-md border-gray-300 shadow-sm"
            :disabled="loading"
          >
            <option value="普通用户">普通用户</option>
            <option value="分销员">分销员</option>
          </select>
        </FormField>

        <template #footer>
          <BaseButtons>
            <BaseButton 
              type="submit" 
              color="info" 
              label="添加" 
              :loading="loading"
              :disabled="loading"
            />
            <BaseButton 
              to="/users" 
              color="info" 
              outline 
              label="取消" 
              :disabled="loading"
            />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-select {
  @apply mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md;
}

.form-select:disabled {
  @apply bg-gray-100 cursor-not-allowed;
}
</style> 
