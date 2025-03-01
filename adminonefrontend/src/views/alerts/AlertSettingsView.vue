<script setup>
import { ref, onMounted } from 'vue'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import BaseButton from '@/components/BaseButton.vue'
import { mdiCog, mdiContentSave } from '@mdi/js'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import api from '@/services/api'

const settings = ref({
  serverHealthCheck: true,
  dockerHealthCheck: true,
  trafficAlert: true,
  emailNotification: true,
  checkInterval: 5,
  thresholds: {
    traffic: 90,
    cpu: 80,
    memory: 80,
    disk: 85
  }
})

// 加载设置
const loadSettings = async () => {
  try {
    const response = await api.getAlertSettings()
    console.log('获取到的设置数据:', response)
    
    if (!response.success) {
      throw new Error(response.message || '加载设置失败')
    }
    
    const data = response.settings || {}
    
    // 转换数据格式
    settings.value = {
      serverHealthCheck: data.serverHealthCheck ?? true,
      dockerHealthCheck: data.dockerHealthCheck ?? true,
      trafficAlert: data.trafficAlert ?? true,
      emailNotification: data.emailNotification ?? true,
      checkInterval: data.checkInterval ?? 5,
      thresholds: {
        traffic: data.thresholds?.traffic ?? 90,
        cpu: data.thresholds?.cpu ?? 80,
        memory: data.thresholds?.memory ?? 80,
        disk: data.thresholds?.disk ?? 85
      }
    }
    
    console.log('转换后的设置数据:', settings.value)
  } catch (error) {
    console.error('加载告警设置失败:', error)
    if (error.response?.data) {
      console.error('错误详情:', error.response.data)
      alert('加载设置失败: ' + (error.response.data.message || '数据格式不正确'))
    } else {
      alert('加载设置失败: ' + error.message)
    }
  }
}

const saveSettings = async () => {
  try {
    // 构造与后端匹配的数据格式
    const requestData = {
      serverHealthCheck: settings.value.serverHealthCheck,
      dockerHealthCheck: settings.value.dockerHealthCheck,
      trafficAlert: settings.value.trafficAlert,
      emailNotification: settings.value.emailNotification,
      checkInterval: parseInt(settings.value.checkInterval),
      thresholds: {
        traffic: parseInt(settings.value.thresholds.traffic),
        cpu: parseInt(settings.value.thresholds.cpu),
        memory: parseInt(settings.value.thresholds.memory),
        disk: parseInt(settings.value.thresholds.disk)
      }
    }
    
    // 添加调试日志
    console.log('发送的设置数据:', requestData)
    
    const response = await api.updateAlertSettings(requestData)
    console.log('服务器响应:', response)
    
    if (response.success) {
      alert('告警设置已成功保存')
    } else {
      throw new Error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    if (error.response?.data) {
      console.error('错误详情:', error.response.data)
      alert('设置保存失败: ' + (error.response.data.message || '数据格式不正确'))
    } else {
      alert('保存设置失败: ' + error.message)
    }
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiCog" title="告警设置" main>
      <BaseButton
        :icon="mdiContentSave"
        color="info"
        @click="saveSettings"
      >
        保存设置
      </BaseButton>
    </SectionTitleLineWithButton>

    <CardBox>
      <div class="space-y-6 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-gray-700 dark:text-gray-300">服务器健康检查</span>
            <span class="ml-2 text-sm text-gray-500">(检测服务器运行状态)</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.serverHealthCheck">
            <span class="slider round"></span>
          </label>
        </div>
        
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-gray-700 dark:text-gray-300">Docker容器检查</span>
            <span class="ml-2 text-sm text-gray-500">(监控容器运行状态)</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.dockerHealthCheck">
            <span class="slider round"></span>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-gray-700 dark:text-gray-300">流量告警</span>
            <span class="ml-2 text-sm text-gray-500">(监控用户流量使用情况)</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.trafficAlert">
            <span class="slider round"></span>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-gray-700 dark:text-gray-300">邮件通知</span>
            <span class="ml-2 text-sm text-gray-500">(发送告警邮件通知)</span>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="settings.emailNotification">
            <span class="slider round"></span>
          </label>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-gray-700 dark:text-gray-300">检查间隔</span>
            <span class="ml-2 text-sm text-gray-500">(多久检查一次，单位：分钟)</span>
          </div>
          <input 
            type="number" 
            v-model="settings.checkInterval" 
            class="w-20 px-2 py-1 border rounded focus:ring-2 focus:ring-blue-500"
            min="1"
            max="60"
          >
        </div>

        <div class="mt-8">
          <h3 class="text-lg font-medium mb-4">告警阈值设置</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="form-group">
              <label>流量使用阈值 (%)</label>
              <input 
                type="number" 
                v-model="settings.thresholds.traffic"
                class="form-input w-full px-3 py-2 border rounded"
                min="0"
                max="100"
              >
            </div>
            <div class="form-group">
              <label>CPU使用率阈值 (%)</label>
              <input 
                type="number" 
                v-model="settings.thresholds.cpu"
                class="form-input w-full px-3 py-2 border rounded"
                min="0"
                max="100"
              >
            </div>
            <div class="form-group">
              <label>内存使用率阈值 (%)</label>
              <input 
                type="number" 
                v-model="settings.thresholds.memory"
                class="form-input w-full px-3 py-2 border rounded"
                min="0"
                max="100"
              >
            </div>
            <div class="form-group">
              <label>磁盘使用率阈值 (%)</label>
              <input 
                type="number" 
                v-model="settings.thresholds.disk"
                class="form-input w-full px-3 py-2 border rounded"
                min="0"
                max="100"
              >
            </div>
          </div>
        </div>
      </div>
    </CardBox>
  </SectionMain>
</template>

<style scoped>
/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:checked + .slider:before {
  transform: translateX(26px);
}
</style> 