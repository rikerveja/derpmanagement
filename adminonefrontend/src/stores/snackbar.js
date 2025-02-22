import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSnackbar = defineStore('snackbar', () => {
  const show = ref(false)
  const message = ref('')
  const color = ref('success')
  const timeout = ref(3000)

  function success(msg) {
    message.value = msg
    color.value = 'success'
    show.value = true
    setTimeout(() => {
      show.value = false
    }, timeout.value)
  }

  function error(msg) {
    message.value = msg
    color.value = 'error'
    show.value = true
    setTimeout(() => {
      show.value = false
    }, timeout.value)
  }

  return {
    show,
    message,
    color,
    success,
    error
  }
}) 