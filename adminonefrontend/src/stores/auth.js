import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token'))

  async function login(username, password) {
    const response = await api.login(username, password)
    token.value = response.token
    localStorage.setItem('token', response.token)
    user.value = response.user
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    login,
    logout
  }
})
