import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  async function login(username, password) {
    const response = await api.login(username, password)
    token.value = response.token
    localStorage.setItem('token', response.token)
    user.value = response.user
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    login,
    logout
  }
}) 