<script setup>
import { ref } from 'vue'
import BaseDialog from '@/components/BaseDialog.vue'
import BaseButton from '@/components/BaseButton.vue'

const props = defineProps({
  show: Boolean,
  rental: Object
})

const emit = defineEmits(['close'])

const formatDate = (date) => {
  return new Date(date).toLocaleString()
}
</script>

<template>
  <BaseDialog
    :show="show"
    @close="$emit('close')"
    :max-width="500"
  >
    <template #header>
      <div class="text-lg font-bold">租赁详情</div>
    </template>

    <template #default>
      <div class="grid gap-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-500">用户ID</label>
            <div>{{ rental?.user_id }}</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">序列号</label>
            <div>{{ rental?.serial_code }}</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">开始时间</label>
            <div>{{ formatDate(rental?.start_date) }}</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">到期时间</label>
            <div>{{ formatDate(rental?.end_date) }}</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">剩余天数</label>
            <div>{{ rental?.days_remaining }}天</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">续费次数</label>
            <div>{{ rental?.renewal_count }}次</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">流量使用</label>
            <div>{{ rental?.traffic_usage || 0 }}GB</div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">流量限制</label>
            <div>{{ rental?.traffic_limit || 0 }}GB</div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end">
        <BaseButton
          color="info"
          label="关闭"
          @click="$emit('close')"
        />
      </div>
    </template>
  </BaseDialog>
</template> 
