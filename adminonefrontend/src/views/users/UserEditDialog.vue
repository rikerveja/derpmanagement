<script setup>
import { ref, watch } from 'vue'
import BaseDialog from '@/components/BaseDialog.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'

const props = defineProps({
  show: Boolean,
  user: Object
})

const emit = defineEmits(['close', 'update'])

const form = ref({
  user_id: '',
  password: '',
  username: '',
  email: '',
  role: '',
  is_banned: false,
  banned_reason: '',
  is_verified: false,
  verification_token: '',
  rental_expiry: '',
  last_login: '',
  new_password: ''
})

// 当对话框打开时，初始化表单数据
watch(() => props.show, (newVal) => {
  if (newVal && props.user) {
    const rental_expiry = props.user.rental_expiry ? 
      new Date(props.user.rental_expiry).toISOString().slice(0, 16) : ''
    
    form.value = {
      user_id: props.user.id,
      password: '',
      new_password: '',
      username: props.user.username,
      email: props.user.email,
      role: props.user.role,
      rental_expiry,
      is_banned: props.user.is_banned,
      banned_reason: props.user.banned_reason,
      is_verified: props.user.is_verified,
      verification_token: props.user.verification_token
    }
  }
})

const loading = ref(false)
const error = ref('')

const roleOptions = [
  { label: '普通用户', value: 'user' },
  { label: '管理员', value: 'admin' },
  { label: '分销员', value: 'distributor' }
]

const handleSubmit = async () => {
  if (!form.value.user_id || !form.value.password) {
    error.value = '请输入验证密码'
    return
  }

  try {
    loading.value = true
    const submitData = {
      user_id: parseInt(form.value.user_id),
      password: form.value.password,
      ...(form.value.email ? { email: form.value.email } : {}),
      ...(form.value.username ? { username: form.value.username } : {}),
      ...(form.value.role ? { role: form.value.role } : {}),
      ...(form.value.rental_expiry ? { rental_expiry: form.value.rental_expiry } : {}),
      ...(typeof form.value.is_banned !== 'undefined' ? { is_banned: Boolean(form.value.is_banned) } : {}),
      ...(form.value.banned_reason ? { banned_reason: form.value.banned_reason } : {}),
      ...(typeof form.value.is_verified !== 'undefined' ? { is_verified: Boolean(form.value.is_verified) } : {}),
      ...(form.value.verification_token ? { verification_token: form.value.verification_token } : {})
    }

    // 如果设置了新密码，则添加到提交数据中
    if (form.value.new_password) {
      submitData.password = form.value.new_password
    }

    // 打印检查提交的数据格式
    console.log('Submitting data:', JSON.stringify(submitData, null, 2))

    const response = await fetch('/api/user/update_info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(submitData)
    })

    const data = await response.json()
    if (data.success) {
      emit('update')
      emit('close')
    } else {
      error.value = data.message || '更新失败'
    }
  } catch (err) {
    console.error('更新用户信息失败:', err)
    error.value = err.message || '更新失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen p-4">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-black opacity-50" @click="$emit('close')"></div>
      
      <!-- 对话框内容 -->
      <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full dark:bg-gray-800">
        <!-- 标题 -->
        <div class="px-6 py-4 border-b dark:border-gray-700">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            修改用户信息
          </h3>
        </div>

        <!-- 表单内容 -->
        <div class="px-6 py-4">
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <FormField label="用户名">
                <FormControl v-model="form.username" placeholder="请输入用户名" />
              </FormField>

              <FormField label="邮箱">
                <FormControl 
                  v-model="form.email" 
                  type="email" 
                  required 
                  placeholder="请输入邮箱"
                />
              </FormField>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <FormField label="角色">
                <select
                  v-model="form.role"
                  class="form-input"
                >
                  <option v-for="option in roleOptions" 
                          :key="option.value" 
                          :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </FormField>

              <FormField label="租约到期">
                <FormControl v-model="form.rental_expiry" type="datetime-local" />
              </FormField>
            </div>

            <FormField label="验证密码" required>
              <FormControl 
                v-model="form.password" 
                type="password" 
                placeholder="请输入当前密码进行验证" 
                required
              />
            </FormField>

            <FormField label="新密码">
              <FormControl 
                v-model="form.new_password" 
                type="password" 
                placeholder="如需修改密码请输入新密码，否则留空" 
              />
            </FormField>

            <div class="grid grid-cols-2 gap-4">
              <FormField label="是否禁用" class="flex-1">
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    v-model="form.is_banned"
                    class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    {{ form.is_banned ? '已禁用' : '未禁用' }}
                  </span>
                </div>
              </FormField>

              <FormField label="是否验证" class="flex-1">
                <div class="flex items-center">
                  <input 
                    type="checkbox" 
                    v-model="form.is_verified"
                    class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    {{ form.is_verified ? '已验证' : '未验证' }}
                  </span>
                </div>
              </FormField>
            </div>

            <FormField v-if="form.is_banned" label="禁用原因">
              <FormControl 
                v-model="form.banned_reason" 
                type="textarea"
                placeholder="请输入禁用原因"
                rows="3"
              />
            </FormField>

            <div v-if="error" class="text-red-600 text-sm mt-2 p-2 bg-red-50 rounded">
              {{ error }}
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end gap-2 dark:bg-gray-700 dark:border-gray-600">
          <BaseButton
            type="button"
            color="info"
            outline
            label="取消"
            :disabled="loading"
            @click="$emit('close')"
          />
          <BaseButton
            type="button"
            color="info"
            :loading="loading"
            :disabled="loading"
            label="保存"
            @click="handleSubmit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm 
         focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
         transition-colors duration-200
         dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300;
}

input[type="checkbox"] {
  @apply rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50;
}

.form-field {
  @apply mb-4;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}
</style> 