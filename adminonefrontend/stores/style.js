import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useStyleStore = defineStore('style', () => {
  // 状态
  const isAsideMobileExpanded = ref(false)
  const isAsideLgActive = ref(true)
  const darkMode = ref(false)

  // Actions
  function asideMobileToggle() {
    isAsideMobileExpanded.value = !isAsideMobileExpanded.value
  }

  function asideLgToggle() {
    isAsideLgActive.value = !isAsideLgActive.value
  }

  function setDarkMode(value = null) {
    darkMode.value = value !== null ? value : !darkMode.value
    localStorage.setItem('darkMode', darkMode.value ? '1' : '0')

    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 初始化主题
  function init() {
    // 从 localStorage 或系统偏好获取主题设置
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const storedDarkMode = localStorage.getItem('darkMode')
    
    if (storedDarkMode !== null) {
      setDarkMode(storedDarkMode === '1')
    } else if (prefersDark) {
      setDarkMode(true)
    }
  }

  return {
    // 状态
    isAsideMobileExpanded,
    isAsideLgActive,
    darkMode,

    // Actions
    asideMobileToggle,
    asideLgToggle,
    setDarkMode,
    init
  }
}) 