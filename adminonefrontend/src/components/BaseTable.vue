<template>
  <div class="base-table">
    <table>
      <slot></slot>
    </table>
  </div>
</template>

<script>
export default {
  name: 'BaseTable'
}
</script>

<style scoped>
.base-table table {
  width: 100%;
  border-collapse: collapse;
}
</style> 
