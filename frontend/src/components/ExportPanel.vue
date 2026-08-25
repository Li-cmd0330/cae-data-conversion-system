<template>
  <div class="toolbar">
    <el-select v-model="format" placeholder="导出格式" style="width: 180px">
      <el-option label="Excel模板" value="excel" />
      <el-option label="JSON" value="json" />
      <el-option label="CSV" value="csv" />
      <el-option label="TXT" value="txt" />
      <el-option label="Abaqus INP" value="abaqus_inp" />
    </el-select>
    <el-button type="primary" :loading="loading" @click="submit">生成导出文件</el-button>
    <el-link v-if="downloadUrl" type="success" :href="downloadUrl" target="_blank">下载文件</el-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { convertMaterial } from '../api/conversion'
const props = defineProps({ materialId: Number })
const format = ref('excel')
const loading = ref(false)
const downloadUrl = ref('')
async function submit() {
  loading.value = true
  try {
    const { data } = await convertMaterial(props.materialId, format.value)
    downloadUrl.value = data.download_url || data.file
  } finally {
    loading.value = false
  }
}
</script>
