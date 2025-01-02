<template>
    <div class="login-view">
      <h2 class="title">{{ isLogin ? '登录' : '注册' }}</h2>
      <form @submit.prevent="handleSubmit">
        <!-- 登录时只显示用户名和密码 -->
        <template v-if="isLogin">
          <div class="form-group">
            <label for="email">邮箱</label>
            <input 
              type="email" 
              id="email"
              v-model="formData.email"
              required
              placeholder="请输入邮箱"
            >
          </div>
  
          <div class="form-group">
            <label for="password">密码</label>
            <input 
              type="password" 
              id="password"
              v-model="formData.password"
              required
              placeholder="请输入密码"
            >
          </div>
        </template>
  
        <!-- 注册时显示所有字段，调整顺序 -->
        <template v-else>
          <div class="form-group">
            <label for="email">邮箱</label>
            <input 
              type="email" 
              id="email"
              v-model="formData.email"
              required
              placeholder="请输入邮箱地址"
              @input="handleEmailInput"
            >
          </div>
  
          <div class="form-group" v-if="formData.email">
            <label>请完成验证</label>
            <slide-verify
              ref="slideVerify"
              @success="onSuccess"
            />
          </div>
  
          <div class="form-group">
            <label for="emailCode">邮箱验证码</label>
            <div class="code-container">
              <input 
                type="text" 
                id="emailCode"
                v-model="formData.emailCode"
                required
                placeholder="请输入邮箱验证码"
                maxlength="6"
              >
              <button 
                type="button" 
                class="send-code-btn" 
                :disabled="countdown > 0 || !verifySuccess"
                @click="sendEmailCode"
              >
                {{ countdown > 0 ? `${countdown}秒后重试` : '重新发送' }}
              </button>
            </div>
          </div>
  
          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              type="text" 
              id="username"
              v-model="formData.username"
              required
              placeholder="请输入用户名"
            >
            <small>用户名长度为4-20个字符</small>
          </div>
  
          <div class="form-group">
            <label for="password">密码</label>
            <input 
              type="password" 
              id="password"
              v-model="formData.password"
              required
              placeholder="请输入密码"
            >
            <small>密码长度至少6位，包含字母和数字</small>
          </div>
  
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input 
              type="password" 
              id="confirmPassword"
              v-model="formData.confirmPassword"
              required
              placeholder="请再次输入密码"
            >
          </div>
        </template>
  
        <div v-if="!isLogin" class="agreement">
          <input 
            type="checkbox" 
            id="agreement" 
            v-model="formData.agreement"
            required
          >
          <label for="agreement">
            我已阅读并同意
            <a href="#" @click.prevent="showTerms">服务条款</a>
            和
            <a href="#" @click.prevent="showPrivacy">隐私政策</a>
          </label>
        </div>
  
        <button type="submit" class="submit-btn">{{ isLogin ? '登录' : '注册' }}</button>
        
        <div class="switch-form">
          <a href="#" @click.prevent="toggleForm">
            {{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}
          </a>
        </div>
      </form>
    </div>
  </template>
  
  <script setup>
  import SlideVerify from '@/components/SlideVerify.vue'
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  
  const authStore = useAuthStore()
  const router = useRouter()
  
  const isLogin = ref(true)
  const verifySuccess = ref(false)
  const countdown = ref(0)
  const emailSending = ref(false)
  const formData = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    emailCode: '',
    agreement: false
  })
  
  const handleSubmit = async () => {
    if (isLogin.value) {
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: formData.value.email,
            password: formData.value.password
          })
        })
  
        const data = await response.json()
        
        if (data.success) {
          localStorage.setItem('token', data.token)
          authStore.user = { 
            email: formData.value.email,
            username: data.username
          }
          localStorage.setItem('user', JSON.stringify(authStore.user))
          authStore.token = data.token
          router.push('/dashboard')
        } else {
          throw new Error(data.message || '登录失败')
        }
      } catch (error) {
        console.error(error)
        alert(error.message)
      }
    } else {
      if (!verifySuccess.value) {
        alert('请先完成滑动验证')
        return
      }
  
      if (!validateForm()) {
        return
      }
  
      try {
        const response = await fetch('/api/add_user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: formData.value.username,
            email: formData.value.email,
            password: formData.value.password,
            verification_code: formData.value.emailCode
          })
        })
  
        const data = await response.json()
        
        if (data.success) {
          alert(data.message || '注册成功！请登录')
          isLogin.value = true
          resetForm()
        } else {
          throw new Error(data.message || '注册失败')
        }
      } catch (error) {
        console.error(error)
        alert(error.message)
      }
    }
  }
  
  const validateForm = () => {
    // 用户名验证
    if (formData.value.username.length < 4 || formData.value.username.length > 20) {
      alert('用户名长度必须在4-20个字符之间')
      return false
    }
  
    // 邮箱验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.value.email)) {
      alert('请输入有效的邮箱地址')
      return false
    }
  
    // 密码验证
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/
    if (!passwordRegex.test(formData.value.password)) {
      alert('密码必须至少包含6个字符，包括字母和数字')
      return false
    }
  
    // 确认密码
    if (formData.value.password !== formData.value.confirmPassword) {
      alert('两次输入的密码不一致')
      return false
    }
  
    return true
  }
  
  const sendEmailCode = async () => {
    if (!formData.value.email) {
      alert('请先输入邮箱地址')
      return
    }
  
    if (!verifySuccess.value) {
      alert('请先完成滑动验证')
      return
    }
  
    // 防止重复发送
    if (emailSending.value || countdown.value > 0) {
      return
    }
  
    try {
      emailSending.value = true
      const response = await fetch('/api/send_verification_email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: formData.value.email
        })
      })
  
      if (response.ok) {
        startCountdown()
      } else {
        const error = await response.json()
        throw new Error(error.message || '发送验证码失败')
      }
    } catch (error) {
      console.error(error)
      alert(error.message)
    } finally {
      emailSending.value = false
    }
  }
  
  const startCountdown = () => {
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  }
  
  const toggleForm = () => {
    const username = formData.value.username
    isLogin.value = !isLogin.value
    resetForm()
    
    if (isLogin.value && username) {
      formData.value.username = username
    }
  
    verifySuccess.value = false
    if (this.$refs.slideVerify) {
      this.$refs.slideVerify.reset()
    }
  }
  
  const resetForm = () => {
    formData.value = {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      emailCode: '',
      agreement: false
    }
  }
  
  const showTerms = () => {
    // 实现显示服务条款的逻辑
    alert('显示服务条款')
  }
  
  const showPrivacy = () => {
    // 实现显示隐私政策的逻辑
    alert('显示隐私政策')
  }
  
  const onSuccess = () => {
    if (!verifySuccess.value) {  // 防止重复触发
      verifySuccess.value = true
      console.log('验证成功')
      
      // 验证成功后自动发送邮箱验证码
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (emailRegex.test(formData.value.email)) {
        sendEmailCode()
      }
    }
  }
  
  const handleEmailInput = () => {
    // 当邮箱输入完整时，重置验证状态
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.value.email)) {
      verifySuccess.value = false
      if (this.$refs.slideVerify) {
        this.$refs.slideVerify.reset()
      }
    }
  }
  </script>
  
  <style scoped>
  .login-view {
    max-width: 460px;
    margin: 40px auto;
    padding: 40px;
    border-radius: 0.25rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  }
  
  .title {
    text-align: center;
    margin-bottom: 2rem;
    color: #2c3e50;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #2c3e50;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  small {
    display: block;
    margin-top: 0.25rem;
    color: #7c858e;
    font-size: 0.75rem;
  }
  
  input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #dcdfe6;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    color: #2c3e50;
    background-color: #fff;
    transition: all 0.3s ease;
  }
  
  input:focus {
    outline: none;
    border-color: #7e3af2;
    box-shadow: 0 0 0 1px rgba(126, 58, 242, 0.2);
  }
  
  .captcha-container, .code-container {
    display: flex;
    gap: 0.75rem;
  }
  
  .captcha-container input, .code-container input {
    width: 60%;
  }
  
  .captcha-image {
    width: 40%;
    height: 42px;
    border: 1px solid #dcdfe6;
    border-radius: 0.25rem;
    cursor: pointer;
    overflow: hidden;
    background-color: #f9fafb;
  }
  
  .captcha-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .send-code-btn {
    width: 40%;
    padding: 0.75rem 1rem;
    background-color: #7e3af2;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    white-space: nowrap;
    transition: background-color 0.3s ease;
  }
  
  .send-code-btn:hover:not(:disabled) {
    background-color: #6c2bd9;
  }
  
  .send-code-btn:disabled {
    background-color: #e5e7eb;
    color: #9ca3af;
    cursor: not-allowed;
  }
  
  .agreement {
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .agreement input[type="checkbox"] {
    width: 1rem;
    height: 1rem;
    border-color: #dcdfe6;
    border-radius: 0.25rem;
    cursor: pointer;
  }
  
  .agreement label {
    margin: 0;
    font-size: 0.875rem;
    color: #4b5563;
    cursor: pointer;
  }
  
  .agreement a {
    color: #7e3af2;
    text-decoration: none;
    font-weight: 500;
  }
  
  .agreement a:hover {
    text-decoration: underline;
  }
  
  .submit-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    background-color: #7e3af2;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background-color 0.3s ease;
  }
  
  .submit-btn:hover {
    background-color: #6c2bd9;
  }
  
  .switch-form {
    text-align: center;
    margin-top: 1.5rem;
  }
  
  .switch-form a {
    color: #7e3af2;
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .switch-form a:hover {
    text-decoration: underline;
  }
  
  /* 响应式调整 */
  @media (max-width: 640px) {
    .login-view {
      margin: 20px;
      padding: 20px;
    }
  }
  
  /* 滑动验证码样式 */
  :deep(.drag-verify-container) {
    margin: 0 auto;
    border: 1px solid #dcdfe6 !important;
    border-radius: 0.25rem !important;
  }
  
  :deep(.drag-verify-text) {
    font-size: 0.875rem !important;
    color: #2c3e50 !important;
  }
  
  :deep(.drag-verify-circle) {
    border-radius: 0.25rem !important;
    box-shadow: 0 2px 6px rgba(126, 58, 242, 0.2) !important;
  }
  </style> 
