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
  mdiDocker,
  mdiContentCopy,
  mdiAccount
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import AclEditDialog from './AclEditDialog.vue'
import AclContentDialog from './AclContentDialog.vue'

const router = useRouter()
const acls = ref([])
const users = ref({})  // 用户信息缓存
const servers = ref({}) // 服务器信息缓存
const containers = ref({}) // 容器信息缓存
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const loading = ref(false)
const showEditDialog = ref(false)
const currentAcl = ref(null)
const showAclDialog = ref(false)
const currentAclContent = ref(null)
const copySuccess = ref(false)

// 获取ACL列表及关联数据
const fetchAcls = async () => {
  try {
    loading.value = true
    const response = await api.getAclConfigs()
    console.log('原始API响应:', response)
    if (response.success) {
      console.log('映射前的 acl_configs:', response.acl_configs)
      
      const mappedConfigs = []
      for (const config of response.acl_configs) {
        console.log('正在处理的配置项:', config)
        const mappedConfig = {
          id: config.id,
          user: config.user,
          servers: config.servers || [],
          containers: config.containers || [],
          version: config.version,
          is_active: config.is_active,
          created_at: config.created_at,
          updated_at: config.updated_at,
          derpMap: config.derpMap,
          acl_data: config.acl_data
        }
        console.log('映射后的配置项:', mappedConfig)
        mappedConfigs.push(mappedConfig)
      }

      // 使用新的方式更新响应式数据
      acls.value = [...mappedConfigs]
      console.log('最终的 acls 数据:', acls.value)

      if (acls.value.length > 0) {
        const firstRecord = acls.value[0]
        console.log('第一条记录详情:', {
          id: firstRecord.id,
          user: firstRecord.user,
          servers: firstRecord.servers,
          containers: firstRecord.containers,
          version: firstRecord.version
        })
      }
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
    const searchLower = searchQuery.value.toLowerCase()
    return acl.user?.email?.toLowerCase().includes(searchLower) ||
           acl.containers?.some(container => 
             container.name.toLowerCase().includes(searchLower)
           )
  })
})

// 分页
const paginatedAcls = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredAcls.value.slice(start, end)
})

// 下载ACL
const downloadAcl = async (acl) => {
  try {
    loading.value = true
    const response = await api.downloadAcl(acl.user.id)
    if (response.success) {
      // 构建格式化的字符串
      const lines = []
      lines.push('    "derpMap": {')
      lines.push('        "OmitDefaultRegions": ' + response.acl.derpMap.OmitDefaultRegions + ',')
      lines.push('        "Regions": {')
      
      // 处理每个区域
      Object.entries(response.acl.derpMap.Regions).forEach(([key, region]) => {
        lines.push(`            "${key}": {`)
        lines.push(`                "RegionID": ${region.RegionID},`)
        lines.push(`                "RegionCode": "${region.RegionCode}",`)
        lines.push(`                "RegionName": "${region.RegionName}",`)
        lines.push('                "Nodes": [')
        
        // 处理节点
        region.Nodes.forEach((node, index) => {
          lines.push('                    {')
          lines.push(`                        "Name": "${node.Name}",`)
          lines.push(`                        "RegionID": ${node.RegionID},`)
          lines.push(`                        "DERPPort": ${node.DERPPort},`)
          lines.push(`                        "ipv4": "${node.ipv4}",`)
          lines.push(`                        "InsecureForTests": ${node.InsecureForTests}`)
          lines.push('                    },')
        })
        
        lines.push('                ],')
        lines.push('            },')
      })
      
      lines.push('        },')
      lines.push('    },')

      currentAclContent.value = lines.join('\n')
      showAclDialog.value = true
    } else {
      throw new Error(response.message || '未找到ACL配置数据')
    }
  } catch (error) {
    console.error('获取ACL配置失败:', error)
    alert('获取ACL配置失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(currentAclContent.value)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
    alert('复制失败: ' + error.message)
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
const editAcl = (acl) => {
  console.log('编辑ACL:', acl)
  currentAcl.value = acl
  showEditDialog.value = true
}

const handleEditSubmit = async () => {
  console.log('编辑提交成功')
  await fetchAcls() // 刷新列表
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
        <BaseButton
          :icon="mdiPlus"
          color="success"
          label="新建ACL"
          to="/acl/generate"
          small
        />
      </SectionTitleLineWithButton>

      <CardBox class="mb-2">
        <!-- 搜索框 -->
        <div class="mb-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索邮箱或容器名称..."
            class="w-full px-2 py-1 border rounded-lg text-sm"
          />
        </div>

        <!-- 表格 -->
        <div class="overflow-x-auto">
          <table class="w-full text-left table-auto text-sm">
            <thead>
              <tr class="border-b">
                <th class="px-2 py-1 w-[20%]">用户</th>
                <th class="px-2 py-1 w-[15%]">服务器</th>
                <th class="px-2 py-1 w-[20%]">容器</th>
                <th class="px-2 py-1 w-[10%]">版本</th>
                <th class="px-2 py-1 whitespace-nowrap w-[10%]">状态</th>
                <th class="px-2 py-1 w-[15%]">更新时间</th>
                <th class="px-2 py-1 text-center w-[10%]">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="acl in paginatedAcls" :key="acl.id" class="border-b">
                <td class="px-2 py-1">
                  <div class="flex items-center">
                    <BaseIcon :path="mdiAccount" class="w-4 h-4 mr-1" />
                    {{ acl.user.email }}
                  </div>
                </td>
                <td class="px-2 py-1">
                  <div class="flex items-center">
                    <BaseIcon :path="mdiServer" class="w-3.5 h-3.5 mr-1" />
                    {{ acl.servers[0]?.ip_address }}
                  </div>
                </td>
                <td class="px-2 py-1">
                  <div class="flex items-center">
                    <BaseIcon :path="mdiDocker" class="w-3.5 h-3.5 mr-1 flex-shrink-0" />
                    <div class="truncate" :title="acl.containers[0]?.name">
                      <!-- 调试信息 -->
                      <template v-if="!acl.containers[0]?.name">
                        <small class="text-gray-500">
                          {{ JSON.stringify(acl.containers[0]) }}
                        </small>
                      </template>
                      <template v-else>
                        {{ acl.containers[0]?.name }}
                      </template>
                    </div>
                  </div>
                </td>
                <td class="px-2 py-1">{{ acl.version }}</td>
                <td class="px-2 py-1">
                  <span 
                    class="inline-flex items-center px-1 py-0.5 rounded-full text-xs"
                    :class="acl.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    <span class="w-1 h-1 mr-0.5 rounded-full" 
                          :class="acl.is_active ? 'bg-green-400' : 'bg-red-400'">
                    </span>
                    {{ acl.is_active ? '活跃' : '禁用' }}
                  </span>
                </td>
                <td class="px-2 py-1 whitespace-nowrap">
                  {{ new Date(acl.updated_at).toLocaleString() }}
                </td>
                <td class="px-2 py-1">
                  <div class="flex justify-center space-x-1">
                    <BaseButton
                      :icon="mdiDownload"
                      color="info"
                      small
                      :disabled="loading"
                      @click="downloadAcl(acl)"
                      title="下载"
                    />
                    <BaseButton
                      :icon="mdiPencil"
                      color="warning"
                      small
                      :disabled="loading"
                      @click="editAcl(acl)"
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
        <div class="mt-1 flex justify-between items-center text-sm">
          <span class="text-gray-600">
            共 {{ acls.length }} 条记录
          </span>
          <div class="flex gap-1">
            <BaseButton
              label="上一页"
              small
              class="px-2 py-1 text-xs"
              :disabled="currentPage === 1"
              @click="currentPage--"
            />
            <BaseButton
              label="下一页"
              small
              class="px-2 py-1 text-xs"
              :disabled="currentPage >= Math.ceil(filteredAcls.length / itemsPerPage)"
              @click="currentPage++"
            />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>

  <AclEditDialog
    :show="showEditDialog"
    :acl-data="currentAcl"
    @close="showEditDialog = false"
    @submit="handleEditSubmit"
  />

  <AclContentDialog
    :show="showAclDialog"
    :content="currentAclContent"
    @close="showAclDialog = false"
  />
</template>

<style scoped>
/* 调整表格行高 */
tr {
  @apply h-7;
}

/* 调整图标大小 */
.w-5 {
  @apply w-3.5;
}
.h-5 {
  @apply h-3.5;
}

/* 调整状态标签的内边距 */
.rounded-full {
  @apply px-1 py-0.5 text-xs;
}

/* 调整表格文字大小 */
table {
  @apply text-sm leading-none;
}

/* 调整按钮大小 */
.space-x-2 > * {
  @apply scale-90;
}

/* 其他样式保持不变 */
pre {
  max-width: 100%;
  overflow-x: auto;
}

.copy-button {
  transition: all 0.2s;
}

.copy-success {
  @apply bg-green-500 text-white;
}
</style> 
