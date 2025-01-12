<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import { mdiShieldAccount, mdiMagnify } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const router = useRouter()
const servers = ref([])
const containers = ref([])
const users = ref([])
const userSearchQuery = ref('')
const serverSearchQuery = ref('')
const containerSearchQuery = ref('')

const form = ref({
  user_id: '',
  server_id: '',
  container_id: ''
})

const filteredUsers = computed(() => {
  const query = userSearchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query)
  )
})

const filteredServers = computed(() => {
  const query = serverSearchQuery.value.toLowerCase()
  return servers.value.filter(server => 
    server.server_name.toLowerCase().includes(query) ||
    server.ip_address.toLowerCase().includes(query) ||
    server.region.toLowerCase().includes(query)
  )
})

const filteredContainers = computed(() => {
  let filtered = containers.value
  
  if (form.value.server_id) {
    const selectedServer = servers.value.find(s => s.id === form.value.server_id)
    if (selectedServer) {
      const ipFormatted = selectedServer.ip_address.replace(/\./g, '_')
      filtered = filtered.filter(container => 
        container.container_name.includes(ipFormatted)
      )
    }
  }
  
  const query = containerSearchQuery.value.toLowerCase()
  if (query) {
    filtered = filtered.filter(container => 
      container.container_name.toLowerCase().includes(query) ||
      container.image.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

const loading = ref(false)
const submitLoading = ref(false)

const fetchData = async () => {
  try {
    loading.value = true
    const [serversRes, containersRes, usersRes] = await Promise.all([
      api.getServers(),
      api.getContainers(),
      api.getAllUsers()
    ])
    if(serversRes.success) {
      servers.value = serversRes.servers
    }
    if(containersRes.success) {
      containers.value = containersRes.containers  
    }
    if(usersRes.success) {
      users.value = usersRes.users
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleServerChange = () => {
  form.value.container_id = ''
}

const submit = async () => {
  try {
    submitLoading.value = true
    const response = await api.generateAcl({
      user_id: form.value.user_id,
      server_id: form.value.server_id,
      container_ids: [form.value.container_id]
    })
    if(response.success) {
      alert('ACL生成成功!')
      router.push('/acl')
    } else {
      alert(response.message)
    }
  } catch (error) {
    console.error('生成ACL失败:', error)
    alert('生成ACL失败: ' + error.message)
  } finally {
    submitLoading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiShieldAccount" title="生成ACL" main>
        <div class="text-sm text-gray-500">
          配置用户的访问控制权限
        </div>
      </SectionTitleLineWithButton>

      <CardBox 
        is-form 
        @submit.prevent="submit"
        class="max-w-4xl mx-auto bg-white dark:bg-gray-800 shadow-lg p-6"
      >
        <div v-if="loading" class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span class="ml-2 text-gray-600">加载中...</span>
        </div>

        <div v-else class="space-y-6">
          <div class="grid grid-cols-1 gap-4">
            <FormField label="用户" help="选择要生成ACL的用户">
              <div class="flex items-center space-x-2">
                <FormControl
                  v-model="userSearchQuery"
                  :icon="mdiMagnify"
                  placeholder="搜索用户名或邮箱..."
                  class="flex-1"
                />
                <select 
                  v-model="form.user_id" 
                  class="form-select flex-1"
                  :class="{'border-red-500': !form.user_id && submitLoading}"
                >
                  <option value="">请选择用户</option>
                  <option 
                    v-for="user in filteredUsers" 
                    :key="user.id" 
                    :value="user.id"
                  >
                    {{ user.username }} ({{ user.email }})
                  </option>
                </select>
              </div>
            </FormField>
          </div>

          <div class="grid grid-cols-2 gap-6">
            <div>
              <FormField label="服务器" help="选择要授权的服务器">
                <FormControl
                  v-model="serverSearchQuery"
                  :icon="mdiMagnify"
                  placeholder="搜索服务器名称、IP或地区..."
                  class="mb-2"
                />
                <div class="border rounded-lg overflow-hidden">
                  <div class="max-h-[300px] overflow-y-auto p-2 space-y-1">
                    <label 
                      v-for="server in filteredServers"
                      :key="server.id"
                      class="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="radio"
                        :value="server.id"
                        v-model="form.server_id"
                        name="server-selection"
                        @change="handleServerChange"
                        class="mr-2"
                      />
                      <div class="flex-1">
                        <div class="font-medium">{{ server.server_name }}</div>
                        <div class="text-sm text-gray-500">
                          {{ server.ip_address }} - {{ server.region }}
                        </div>
                      </div>
                    </label>
                  </div>
                </div>
                <div v-if="form.server_id" class="mt-2 text-sm text-gray-500">
                  已选择服务器: {{ servers.find(s => s.id === form.server_id)?.server_name }}
                </div>
              </FormField>
            </div>

            <div>
              <FormField label="容器" help="选择要授权的容器">
                <FormControl
                  v-model="containerSearchQuery"
                  :icon="mdiMagnify"
                  placeholder="搜索容器名称或镜像..."
                  class="mb-2"
                  :disabled="!form.server_id"
                />
                <div class="border rounded-lg overflow-hidden">
                  <div class="max-h-[300px] overflow-y-auto p-2 space-y-1">
                    <div v-if="!form.server_id" class="p-4 text-center text-gray-500">
                      请先选择服务器
                    </div>
                    <label 
                      v-else
                      v-for="container in filteredContainers"
                      :key="container.id"
                      class="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="radio"
                        :value="container.id"
                        v-model="form.container_id"
                        name="container-selection"
                        class="mr-2"
                      />
                      <div class="flex-1">
                        <div class="font-medium">{{ container.container_name }}</div>
                        <div class="text-sm text-gray-500">{{ container.image }}</div>
                      </div>
                    </label>
                  </div>
                </div>
                <div v-if="form.container_id" class="mt-2 text-sm text-gray-500">
                  已选择容器: {{ containers.value.find(c => c.id === form.container_id)?.container_name }}
                </div>
              </FormField>
            </div>
          </div>

          <div class="flex justify-end space-x-4 pt-4 border-t">
            <BaseButton 
              to="/acl" 
              color="info" 
              outline 
              label="取消"
              class="min-w-[100px]" 
            />
            <BaseButton 
              type="submit" 
              color="info" 
              label="生成"
              :loading="submitLoading"
              :disabled="!form.user_id || !form.server_id || !form.container_id"
              class="min-w-[100px]"
            />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
.form-select {
  @apply mt-1 block w-full rounded-lg border-gray-300 shadow-sm 
    focus:border-indigo-500 focus:ring-indigo-500
    transition-all duration-200;
}

.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.400') theme('colors.gray.100');
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-gray-400 rounded hover:bg-gray-500;
}

input[type="radio"] {
  @apply w-4 h-4 text-blue-600 rounded-full border-gray-300 
    focus:ring-blue-500 cursor-pointer;
}

label:hover {
  @apply bg-gray-50;
}
</style> 
