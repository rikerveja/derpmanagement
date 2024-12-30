<template>
  <div class="auth-container">
    <h2>登录</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">用户名或邮箱</label>
        <input v-model="loginForm.username" type="text" id="username" required />
      </div>
      <div>
        <label for="password">密码</label>
        <input v-model="loginForm.password" type="password" id="password" required />
      </div>
      <button type="submit">登录</button>
      <p><router-link to="/users/add">注册新用户</router-link></p>
    </form>

    <h2>注册</h2>
    <form @submit.prevent="register">
      <div>
        <label for="reg-username">用户名</label>
        <input v-model="registerForm.username" type="text" id="reg-username" required />
      </div>
      <div>
        <label for="reg-email">邮箱</label>
        <input v-model="registerForm.email" type="email" id="reg-email" required />
      </div>
      <div>
        <label for="reg-password">密码</label>
        <input v-model="registerForm.password" type="password" id="reg-password" required />
      </div>
      <div>
        <label for="reg-confirm-password">确认密码</label>
        <input v-model="registerForm.confirmPassword" type="password" id="reg-confirm-password" required />
      </div>
      <div>
        <label for="reg-role">角色</label>
        <select v-model="registerForm.role" id="reg-role" required>
          <option value="普通用户">普通用户</option>
          <option value="分销员">分销员</option>
        </select>
      </div>
      <button type="submit">注册</button>
      <p><router-link to="/login">返回登录</router-link></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: '普通用户' // 默认角色
})

const login = async () => {
  // 登录逻辑
  try {
    await api.login(loginForm.value)
    router.push('/dashboard') // 登录成功后跳转
  } catch (error) {
    console.error('登录失败:', error)
  }
}

const register = async () => {
  // 注册逻辑
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    alert('密码不匹配')
    return
  }
  try {
    await api.register(registerForm.value)
    router.push('/login') // 注册成功后跳转到登录
  } catch (error) {
    console.error('注册失败:', error)
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: auto;
}
</style> 
