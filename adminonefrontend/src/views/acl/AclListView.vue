<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiShieldAccount, 
  mdiDownload, 
  mdiPencil,
  mdiDelete,
  mdiRefresh,
  mdiPlus,
  mdiServer,
  mdiDocker
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const acls = ref([])
const users = ref({})  // 用户信息缓存
const servers = ref({}) // 服务器信息缓存
const containers = ref({}) // 容器信息缓存
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const loading = ref(false)

// 获取ACL列表及关联数据
const fetchAcls = async () => {
  try {
    loading.value = true
    const response = await api.getAclList()
    if (response.success) {
      acls.value = await Promise.all(response.acls.map(async acl => {
        // 获取用户信息
        if (!users.value[acl.user_id]) {
          const userResponse = await api.getUser(acl.user_id)
          users.value[acl.user_id] = userResponse.data
        }
        
        // 获取服务器信息
        for (const serverId of acl.server_ids) {
          if (!servers.value[serverId]) {
            const serverResponse = await api.getServer(serverId)
            servers.value[serverId] = serverResponse.data
          }
        }
        
        // 获取容器信息
        for (const containerId of acl.container_ids) {
          if (!containers.value[containerId]) {
            const containerResponse = await api.getContainer(containerId)
            containers.value[containerId] = containerResponse.data
          }
        }
        
        return acl
      }))
    }
  } catch (error) {
    console.error('获取ACL数据失败:', error)
    alert('获取ACL数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 筛选ACL
const filteredAcls = computed(() => {
  return acls.value.filter(acl => {
    const user = users.value[acl.user_id]
    const searchLower = searchQuery.value.toLowerCase()
    return user?.username?.toLowerCase().includes(searchLower) ||
           acl.version?.toLowerCase().includes(searchLower)
  })
})

// 分页
const paginatedAcls = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredAcls.value.slice(start, end)
})

// 下载ACL
const downloadAcl = async (aclId) => {
  try {
    loading.value = true
    const response = await api.downloadAcl(aclId)
    if(response.success) {
      // 创建下载链接
      const blob = new Blob([JSON.stringify(response.acl, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `acl_${aclId}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('下载ACL失败:', error)
    alert('下载ACL失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 删除ACL
const deleteAcl = async (aclId) => {
  if (confirm('确定要删除此ACL吗？')) {
    try {
      loading.value = true
      const response = await api.deleteAcl(aclId)
      if(response.success) {
        alert('删除成功!')
        await fetchAcls()
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      console.error('删除ACL失败:', error)
      alert('删除ACL失败: ' + error.message)
    } finally {
      loading.value = false
    }
  }
}

// 编辑ACL
const editAcl = (aclId) => {
  router.push(`/acl/edit/${aclId}`)
}

// 创建新ACL
const createAcl = () => {
  router.push('/acl/generate')
}

onMounted(() => {
  fetchAcls()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiShieldAccount" title="ACL管理" main>
        <BaseButton :icon="mdiPlus" label="新建ACL" color="success" @click="createAcl" />
        <BaseButton :icon="mdiRefresh" label="刷新" @click="fetchAcls" />
      </SectionTitleLineWithButton>

      <CardBox>
        <!-- 搜索栏 -->
        <div class="mb-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户名或版本..."
            class="w-full px-4 py-2 border rounded-lg"
          >
        </div>

        <!-- ACL列表 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left">用户</th>
                <th class="px-4 py-3 text-left">服务器</th>
                <th class="px-4 py-3 text-left">容器</th>
                <th class="px-4 py-3 text-left">版本</th>
                <th class="px-4 py-3 text-left">状态</th>
                <th class="px-4 py-3 text-left">更新时间</th>
                <th class="px-4 py-3 text-left">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-if="loading">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  <div class="flex items-center justify-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
                    <span class="ml-2">加载中...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="acls.length === 0">
                <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                  暂无ACL数据
                </td>
              </tr>
              <tr v-for="acl in paginatedAcls" :key="acl.id" class="hover:bg-gray-50">
                <!-- 用户信息 -->
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <span class="font-medium">{{ users[acl.user_id]?.username }}</span>
                  </div>
                </td>

                <!-- 服务器信息 -->
                <td class="px-4 py-3">
                  <div class="flex flex-col gap-1">
                    <div v-for="serverId in acl.server_ids" :key="serverId"
                         class="flex items-center gap-1 text-sm">
                      <BaseIcon :path="mdiServer" size="16" />
                      <span>{{ servers[serverId]?.ip_address }}</span>
                    </div>
                  </div>
                </td>

                <!-- 容器信息 -->
                <td class="px-4 py-3">
                  <div class="flex flex-col gap-1">
                    <div v-for="containerId in acl.container_ids" :key="containerId"
                         class="flex items-center gap-1 text-sm">
                      <BaseIcon :path="mdiDocker" size="16" />
                      <span>{{ containers[containerId]?.container_name }}</span>
                    </div>
                  </div>
                </td>

                <!-- 版本信息 -->
                <td class="px-4 py-3">
                  <span class="text-sm">v{{ acl.version }}</span>
                </td>

                <!-- 状态 -->
                <td class="px-4 py-3">
                  <span :class="`px-2 py-1 rounded-full text-xs ${
                    acl.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`">
                    {{ acl.is_active ? '活跃' : '禁用' }}
                  </span>
                </td>

                <!-- 更新时间 -->
                <td class="px-4 py-3">
                  <span class="text-sm">
                    {{ new Date(acl.updated_at).toLocaleString() }}
                  </span>
                </td>

                <!-- 操作按钮 -->
                <td class="px-4 py-3">
                  <div class="flex space-x-2">
                    <BaseButton
                      :icon="mdiDownload"
                      color="info"
                      small
                      :disabled="loading"
                      @click="downloadAcl(acl.id)"
                      title="下载"
                    />
                    <BaseButton
                      :icon="mdiPencil"
                      color="warning"
                      small
                      :disabled="loading"
                      @click="editAcl(acl.id)"
                      title="编辑"
                    />
                    <BaseButton
                      :icon="mdiDelete"
                      color="danger"
                      small
                      :disabled="loading"
                      @click="deleteAcl(acl.id)"
                      title="删除"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <div class="mt-4 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            共 {{ acls.length }} 条记录
          </span>
          <div class="flex gap-2">
            <BaseButton
              label="上一页"
              :disabled="currentPage === 1"
              @click="currentPage--"
            />
            <BaseButton
              label="下一页"
              :disabled="currentPage >= Math.ceil(filteredAcls.length / itemsPerPage)"
              @click="currentPage++"
            />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template> 
