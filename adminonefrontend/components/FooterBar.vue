<script setup>
import { containerMaxW } from '@/config.js'
import BaseLevel from '@/components/BaseLevel.vue'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="py-2 px-6" :class="containerMaxW">
    <BaseLevel>
      <div class="text-center md:text-left">
        <b>&copy;{{ year }}, ZhangJiayuan.</b>
        &nbsp;
        <a href="http://jiayuanhome.cc" target="_blank">jiayuanhome.cc</a>
      </div>
    </BaseLevel>
  </footer>
</template>
