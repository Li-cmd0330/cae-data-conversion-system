<template>
  <el-card class="page-card">
    <h1 class="page-title">格式转换与文件导出</h1>
    <el-alert title="可选择一个或多个已解析材料，同时生成对应结果文件。导出文件名与源 KEY 文件名一致，仅替换扩展名。" type="info" show-icon :closable="false" />

    <div class="toolbar" style="margin-top: 16px">
      <el-select v-model="targetFormat" placeholder="导出格式" style="width: 180px">
        <el-option label="Excel模板" value="excel" />
        <el-option label="JSON" value="json" />
        <el-option label="CSV" value="csv" />
        <el-option label="TXT" value="txt" />
        <el-option label="Abaqus INP" value="abaqus_inp" />
      </el-select>
      <el-button @click="loadMaterials">刷新材料列表</el-button>
      <el-button type="primary" :disabled="!selectedRows.length" :loading="loading" @click="batchExport">批量生成结果文件</el-button>
    </div>

    <el-table :data="materials" border stripe @selection-change="selectedRows = $event">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="材料ID" width="90" />
      <el-table-column prop="file.filename" label="源文件名" min-width="240" />
      <el-table-column prop="name" label="材料名称" min-width="180" />
      <el-table-column prop="unit_system" label="单位系统" width="100" />
    </el-table>

    <template v-if="exports.length">
      <el-divider />
      <h2>生成结果</h2>
      <el-table :data="exports" border stripe>
        <el-table-column prop="material" label="材料ID" width="90" />
        <el-table-column prop="filename" label="结果文件名" min-width="240" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="下载" width="140">
          <template #default="scope">
            <el-link type="primary" :href="scope.row.download_url" target="_blank">下载</el-link>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { batchConvertMaterials, listMaterials } from '../api/material'
const materials = ref([])
const selectedRows = ref([])
const exports = ref([])
const targetFormat = ref('excel')
const loading = ref(false)
async function loadMaterials() {
  const { data } = await listMaterials()
  materials.value = data.results || data
}
async function batchExport() {
  loading.value = true
  try {
    const ids = selectedRows.value.map(item => item.id)
    const { data } = await batchConvertMaterials(ids, targetFormat.value)
    exports.value = data.results || []
  } finally {
    loading.value = false
  }
}
onMounted(loadMaterials)
</script>
