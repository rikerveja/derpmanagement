import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useMainStore } from '@/stores/main.js'
import { useStyleStore } from '@/stores/style.js'
import './css/main.css'

// 创建应用
const app = createApp(App)

// 初始化 Pinia
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 初始化 store
const mainStore = useMainStore()
const styleStore = useStyleStore()

// 初始化暗色主题
styleStore.init()

// 修改默认标题
const defaultDocumentTitle = 'Derp Manager'

// 设置文档标题
router.afterEach((to) => {
  document.title = to.meta?.title
    ? `${to.meta.title} — ${defaultDocumentTitle}`
    : defaultDocumentTitle
})

app.mount('#app')
