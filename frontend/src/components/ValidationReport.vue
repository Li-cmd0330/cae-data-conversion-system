<template>
  <div class="report-grid">
    <el-alert v-for="msg in report.errors || []" :key="msg" type="error" :title="msg" show-icon :closable="false" />
    <el-alert v-for="msg in report.warnings || []" :key="msg" type="warning" :title="msg" show-icon :closable="false" />
    <el-alert v-for="msg in report.info || []" :key="msg" type="info" :title="msg" show-icon :closable="false" />
  </div>
</template>

<script setup>
defineProps({ report: { type: Object, default: () => ({}) } })
</script>

<style scoped>
.report-grid { display: grid; gap: 10px; }
</style>
