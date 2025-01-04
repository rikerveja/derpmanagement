import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { useMainStore } from './main'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token'))
  const mainStore = useMainStore()

  async function login(email, password) {
    try {
      const response = await api.login(email, password)
      
      // 构造用户信息对象
      const userData = {
        email: email,
        username: response.data?.username || email.split('@')[0], // 如果后端没返回username，使用邮箱前缀
        ...response.data // 合并后端返回的其他用户数据
      }
      
      // 保存 token
      token.value = response.token
      localStorage.setItem('token', response.token)
      
      // 保存用户信息
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      
      // 更新 main store 中的用户信息
      mainStore.setUser({
        email: userData.email,
        username: userData.username
      })

      return response
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    mainStore.clearUser() // 确保清除 main store 中的用户信息
  }

  return {
    user,
    token,
    login,
    logout
  }
})
