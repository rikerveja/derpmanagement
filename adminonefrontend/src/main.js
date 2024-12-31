import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './css/main.css'

// 禁用页面可见性变化时的自动刷新
document.addEventListener('visibilitychange', (e) => {
  e.preventDefault()
  return false
}, false)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
