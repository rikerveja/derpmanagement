<script setup>
import { ref, computed, onMounted } from 'vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import { 
  mdiAccountMultiple,
  mdiInformation,
  mdiHistory,
  mdiDownload,
  mdiBellRing,
  mdiRefresh,
  mdiPlus,
  mdiMagnify,
  mdiPencil,
  mdiChartLine
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'
import UserEditDialog from './UserEditDialog.vue'

// 添加 loading 状态
const loading = ref(false)

// 用户数据
const users = ref([])
const currentPage = ref(1)
const itemsPerPage = 10

// 搜索条件
const searchQuery = ref({
  keyword: '',  // 统一的搜索关键字，用于用户名和邮箱
  role: ''      // 角色筛选
})

// 排序相关状态
const sortConfig = ref({
  key: 'username',
  order: 'asc'
})

// 过滤后的用户列表
const filteredUsers = computed(() => {
  let result = users.value

  // 搜索过滤
  if (searchQuery.value.keyword) {
    const keyword = searchQuery.value.keyword.toLowerCase()
    result = result.filter(user => {
      return user.username.toLowerCase().includes(keyword) ||
             user.email.toLowerCase().includes(keyword)
    })
  }

  // 角色过滤
  if (searchQuery.value.role) {
    result = result.filter(user => user.role === searchQuery.value.role)
  }

  // 排序
  result = [...result].sort((a, b) => {
    let compareResult = 0
    switch (sortConfig.value.key) {
      case 'username':
        compareResult = a.username.localeCompare(b.username)
        break
      case 'email':
        compareResult = a.email.localeCompare(b.email)
        break
      case 'last_login':
        compareResult = new Date(a.last_login || 0) - new Date(b.last_login || 0)
        break
      default:
        compareResult = 0
    }
    return sortConfig.value.order === 'desc' ? -compareResult : compareResult
  })

  return result
})

// 分页数据
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredUsers.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => 
  Math.ceil(filteredUsers.value.length / itemsPerPage)
)

// 处理排序
const handleSort = (key) => {
  if (sortConfig.value.key === key) {
    sortConfig.value.order = sortConfig.value.order === 'asc' ? 'desc' : 'asc'
  } else {
    sortConfig.value.key = key
    sortConfig.value.order = 'asc'
  }
}

// 刷新数据
const refreshData = async () => {
  try {
    loading.value = true
    console.log('开始刷新用户数据')
    const response = await api.getAllUsers()
    console.log('获取到的用户数据:', response)
    
    if (response.success && Array.isArray(response.users)) {
      users.value = response.users
    } else {
      console.error('用户数据格式不符合预期:', response)
      users.value = []
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    users.value = []
  } finally {
    loading.value = false
  }
}

// 添加编辑对话框状态
const showEditDialog = ref(false)
const currentUser = ref(null)

// 修改编辑用户信息函数
const editUserInfo = async (userId) => {
  // 打印一下看看是否能找到用户数据
  console.log('当前用户列表:', users.value)
  console.log('要编辑的用户ID:', userId)
  
  const userToEdit = users.value.find(user => user.id === userId)
  console.log('找到的用户数据:', userToEdit)
  
  if (userToEdit) {
    currentUser.value = userToEdit
    showEditDialog.value = true
  } else {
    console.error('未找到用户数据')
  }
}

// 处理用户信息更新
const handleUserUpdate = () => {
  refreshData() // 刷新用户列表
}

const viewTrafficDetails = async (userId) => {
  try {
    const trafficInfo = await api.getUserTraffic(userId)
    console.log('流量详情:', trafficInfo)
  } catch (error) {
    console.error('获取流量详情失败:', error)
  }
}

const downloadAcl = async (userId) => {
  try {
    await api.downloadAcl(userId)
  } catch (error) {
    console.error('下载ACL失败:', error)
  }
}

const sendReminder = async (userId) => {
  try {
    await api.sendReminderNotification({ userId })
    console.log('续费通知已发送')
  } catch (error) {
    console.error('发送续费通知失败:', error)
  }
}

onMounted(() => {
  refreshData()
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <CardBox class="mb-6 dark:bg-gray-900">
        <!-- 标题和操作按钮 -->
        <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <h1 class="text-2xl font-bold dark:text-white">用户管理</h1>
          <div class="flex flex-wrap gap-2">
            <BaseButton
              :icon="mdiRefresh"
              color="info"
              @click="refreshData"
              :loading="loading"
              title="刷新"
              class="whitespace-nowrap"
            />
            <BaseButton
              :icon="mdiPlus"
              color="success"
              label="添加用户"
              :to="`/users/add`"
              class="whitespace-nowrap"
            />
          </div>
        </div>

        <!-- 搜索区域 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div class="form-group">
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">搜索</label>
            <input
              v-model="searchQuery.keyword"
              type="text"
              class="form-input dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700"
              placeholder="搜索用户名/邮箱"
            />
          </div>
          <div class="form-group">
            <label class="block text-sm font-medium mb-2 dark:text-gray-300">角色</label>
            <select 
              v-model="searchQuery.role" 
              class="form-input dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700"
            >
              <option value="">全部</option>
              <option value="普通用户">普通用户</option>
              <option value="分销员">分销员</option>
            </select>
          </div>
        </div>

        <!-- 用户列表 -->
        <CardBox>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th @click="handleSort('username')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">用户名</th>
                  <th @click="handleSort('email')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">Email</th>
                  <th @click="handleSort('role')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">角色</th>
                  <th @click="handleSort('rental_expiry')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">租约到期</th>
                  <th @click="handleSort('last_login')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">登陆时间</th>
                  <th @click="handleSort('isVerified')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">验证</th>
                  <th class="px-4 py-2 text-center text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.username }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.email }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.role }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.rental_expiry }}</td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.last_login }}</td>
                  <td class="px-4 py-3">
                    <span :class="{
                      'px-2 py-1 rounded-full text-xs': true,
                      'bg-green-100 text-green-800': user.is_verified,
                      'bg-red-100 text-red-800': !user.is_verified
                    }">
                      {{ user.is_verified ? '已验证' : '未验证' }}
                    </span>
                  </td>
                  <td class="px-4 py-2 whitespace-nowrap text-sm text-center">
                    <div class="flex justify-center space-x-2">
                      <button 
                        @click="editUserInfo(user.id)" 
                        class="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                        title="修改信息"
                      >
                        <BaseIcon :path="mdiPencil" size="18" />
                      </button>
                      <button 
                        @click="viewTrafficDetails(user.id)" 
                        class="text-green-600 hover:text-green-800 dark:text-green-400"
                        title="流量详情"
                      >
                        <BaseIcon :path="mdiChartLine" size="18" />
                      </button>
                      <button 
                        @click="downloadAcl(user.id)" 
                        class="text-purple-600 hover:text-purple-800 dark:text-purple-400"
                        title="下载ACL"
                      >
                        <BaseIcon :path="mdiDownload" size="18" />
                      </button>
                      <button 
                        @click="sendReminder(user.id)" 
                        class="text-orange-600 hover:text-orange-800 dark:text-orange-400"
                        title="续费通知"
                      >
                        <BaseIcon :path="mdiBellRing" size="18" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页控件 -->
          <div class="mt-4 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="text-sm text-gray-700 dark:text-gray-300">
              共 {{ filteredUsers.length }} 个用户
            </div>
            <div class="flex items-center space-x-2">
              <BaseButton
                :disabled="currentPage === 1"
                @click="currentPage--"
                label="上一页"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
              />
              <span class="px-4 py-2">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <BaseButton
                :disabled="currentPage >= totalPages"
                @click="currentPage++"
                label="下一页"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage >= totalPages }"
              />
            </div>
          </div>
        </CardBox>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>

  <!-- 添加编辑对话框 -->
  <UserEditDialog
    :show="showEditDialog"
    :user="currentUser"
    @close="showEditDialog = false"
    @update="handleUserUpdate"
  />
</template> 

<style scoped>
.form-group {
  @apply relative;
}

.form-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm 
         focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
         transition-colors duration-200
         dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300;
}

.form-input:disabled {
  @apply bg-gray-100 cursor-not-allowed
         dark:bg-gray-700 dark:text-gray-500;
}

/* 工具提示样式 */
button {
  position: relative;
}

button:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 10;
}
</style> 
