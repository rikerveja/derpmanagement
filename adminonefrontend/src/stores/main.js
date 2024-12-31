import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useMainStore = defineStore('main', () => {
  const userEmail = ref(localStorage.getItem('userEmail') || '')
  const userName = ref(localStorage.getItem('userName') || '')

  const userAvatar = computed(
    () =>
      `https://api.dicebear.com/7.x/avataaars/svg?seed=${userEmail.value.replace(
        /[^a-z0-9]+/gi,
        '-'
      )}`
  )

  const isFieldFocusRegistered = ref(false)

  const clients = ref([])
  const history = ref([])

  function setUser(payload) {
    if (payload.email) {
      userEmail.value = payload.email
      localStorage.setItem('userEmail', payload.email)
    }
    if (payload.username) {
      userName.value = payload.username
      localStorage.setItem('userName', payload.username)
    }
  }

  function clearUser() {
    userEmail.value = ''
    userName.value = ''
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userName')
    localStorage.removeItem('token')
  }

  function fetchSampleClients() {
    axios
      .get(`data-sources/clients.json?v=3`)
      .then((result) => {
        clients.value = result?.data?.data
      })
      .catch((error) => {
        alert(error.message)
      })
  }

  function fetchSampleHistory() {
    axios
      .get(`data-sources/history.json`)
      .then((result) => {
        history.value = result?.data?.data
      })
      .catch((error) => {
        alert(error.message)
      })
  }

  return {
    userName,
    userEmail,
    userAvatar,
    isFieldFocusRegistered,
    clients,
    history,
    setUser,
    clearUser,
    fetchSampleClients,
    fetchSampleHistory
  }
})
