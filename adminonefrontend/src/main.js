import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './css/main.css'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
app.use(createPinia())
app.use(router)

const authStore = useAuthStore()

// 恢复用户信息
const user = JSON.parse(localStorage.getItem('user'))
if (user) {
  authStore.user = user
  authStore.token = user.token
}

app.mount('#app')
