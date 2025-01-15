<script setup>
import { ref, watch } from 'vue'
import BaseDialogR from '@/components/BaseDialogR.vue'
import BaseButton from '@/components/BaseButton.vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  rental: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'renew'])

const renewalForm = ref({
  serial_code: '',
  renewal_amount: 0,
  renewal_period: 30
})

const handleRenew = () => {
  if (!renewalForm.value.renewal_amount || !renewalForm.value.renewal_period) {
    alert('请填写完整的续费信息')
    return
  }
  emit('renew', renewalForm.value)
}

// 监听 rental 变化，更新表单
watch(() => props.rental, (newRental) => {
  if (newRental) {
    renewalForm.value.serial_code = newRental.serial_code
  }
}, { immediate: true })
</script>

<template>
  <BaseDialogR
    :show="show"
    @close="handleClose"
  >
    <template #header>
      <div class="text-lg font-bold">续费租赁</div>
    </template>

    <template #default>
      <div class="grid gap-4">
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">序列号</label>
          <input
            v-model="renewalForm.serial_code"
            type="text"
            class="w-full px-3 py-2 border rounded-md"
            disabled
          />
        </div>

        <div class="form-group">
          <label class="block text-sm font-medium mb-2">续费金额 <span class="text-red-500">*</span></label>
          <input
            v-model.number="renewalForm.renewal_amount"
            type="number"
            min="0"
            step="0.01"
            class="w-full px-3 py-2 border rounded-md"
            placeholder="请输入续费金额"
          />
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium mb-2">续费时长(天) <span class="text-red-500">*</span></label>
          <input
            v-model.number="renewalForm.renewal_period"
            type="number"
            min="1"
            class="w-full px-3 py-2 border rounded-md"
            placeholder="请输入续费时长"
          />
        </div>

        <div class="text-sm text-gray-500">
          注意：续费后将自动延长租赁期限，并更新相关记录。
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end space-x-2">
        <BaseButton
          color="info"
          label="取消"
          @click="$emit('close')"
        />
        <BaseButton
          color="success"
          label="确认续费"
          @click="handleRenew"
        />
      </div>
    </template>
  </BaseDialogR>
</template>

<style scoped>
.form-group {
  @apply mb-4;
}

input[type="number"] {
  @apply [appearance:textfield];
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  @apply appearance-none m-0;
}
</style> 
