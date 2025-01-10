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
  mdiRefresh 
} from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseIcon from '@/components/BaseIcon.vue'
import api from '@/services/api'

// 用户数据
const users = ref([])
const currentPage = ref(1)
const itemsPerPage = 10
const sortKey = ref('username')
const sortOrder = ref(1)

// 计算分页数据
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return users.value.slice(start, end)
})

// 排序函数
const sortData = (data, key) => {
  if (sortKey.value === key) {
    sortOrder.value *= -1
  } else {
    sortKey.value = key
    sortOrder.value = 1
  }
  data.sort((a, b) => {
    // 对于日期类型的字段进行特殊处理
    if (key === 'rental_expiry' || key === 'last_login') {
      return (new Date(a[key] || 0) - new Date(b[key] || 0)) * sortOrder.value
    }
    if (a[key] < b[key]) return -1 * sortOrder.value
    if (a[key] > b[key]) return 1 * sortOrder.value
    return 0
  })
}

// 刷新数据
const refreshData = async () => {
  try {
    console.log('开始刷新用户数据')
    const response = await api.getAllUsers()
    console.log('获取到的用户数据:', response)
    
    if (response && Array.isArray(response)) {
      users.value = response
    } else if (response && Array.isArray(response.data)) {
      users.value = response.data
    } else if (response && response.users && Array.isArray(response.users)) {
      users.value = response.users
    } else {
      console.error('用户数据格式不符合预期:', response)
      users.value = []
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    users.value = []
  }
}

// 用户操作函数
const viewRentalInfo = async (userId) => {
  try {
    const rentalInfo = await api.getRentalInfo(userId)
    console.log('租赁详情:', rentalInfo)
  } catch (error) {
    console.error('获取租赁详情失败:', error)
  }
}

const viewRentalHistory = async (userId) => {
  try {
    const rentalHistory = await api.getRentalHistory(userId)
    console.log('租赁历史:', rentalHistory)
  } catch (error) {
    console.error('获取租赁历史失败:', error)
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
      <SectionTitleLineWithButton :icon="mdiAccountMultiple" title="用户管理" main>
        <BaseButton :icon="mdiRefresh" label="刷新" @click="refreshData" />
      </SectionTitleLineWithButton>

      <!-- 用户列表 -->
      <CardBox>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th @click="sortData(users, 'username')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">用户名</th>
                <th @click="sortData(users, 'email')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">Email</th>
                <th @click="sortData(users, 'role')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">角色</th>
                <th @click="sortData(users, 'rental_expiry')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">租约到期</th>
                <th @click="sortData(users, 'last_login')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">登陆时间</th>
                <th @click="sortData(users, 'isVerified')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">验证</th>
                <th @click="sortData(users, 'verificationCode')" class="px-4 py-2 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer">序列号</th>
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
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.isVerified ? '是' : '否' }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{{ user.verificationCode }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-center">
                  <div class="flex justify-center space-x-2">
                    <button 
                      @click="viewRentalInfo(user.id)" 
                      class="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      title="租赁详情"
                    >
                      <BaseIcon :path="mdiInformation" size="18" />
                    </button>
                    <button 
                      @click="viewRentalHistory(user.id)" 
                      class="text-green-600 hover:text-green-800 dark:text-green-400"
                      title="租赁历史"
                    >
                      <BaseIcon :path="mdiHistory" size="18" />
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
        <div class="mt-4 flex justify-between items-center">
          <span class="text-sm text-gray-600">
            共 {{ users.length }} 个用户
          </span>
          <div class="space-x-2">
            <BaseButton @click="currentPage--" :disabled="currentPage === 1" label="上一页" />
            <BaseButton @click="currentPage++" :disabled="currentPage * itemsPerPage >= users.length" label="下一页" />
          </div>
        </div>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>

<style scoped>
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
