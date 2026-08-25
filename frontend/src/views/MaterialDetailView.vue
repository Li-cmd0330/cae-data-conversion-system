<template>
  <el-card class="page-card">
    <h1 class="page-title">材料详情与可视化</h1>
    <div class="toolbar">
      <el-select v-model="selectedId" placeholder="选择材料" @change="loadMaterial" style="width: 320px">
        <el-option v-for="item in materials" :key="item.id" :label="item.name || item.file?.filename" :value="item.id" />
      </el-select>
      <el-button @click="loadList">刷新</el-button>
      <el-button type="danger" plain :disabled="!materials.length" @click="confirmClearHistory">清空历史材料</el-button>
    </div>
    <el-alert v-if="!materials.length" title="当前没有历史材料文件，请先在文件上传页面上传 KEY 文件。" type="info" show-icon :closable="false" />
    <template v-if="material">
      <el-descriptions border :column="3">
        <el-descriptions-item label="材料名称">{{ material.name }}</el-descriptions-item>
        <el-descriptions-item label="单位系统">{{ material.unit_system }}</el-descriptions-item>
        <el-descriptions-item label="文件名">{{ material.file?.filename }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <MaterialPropertyTable :data="material.normalized_data" />
      <el-divider />
      <FlowStressChart :chart="chart" />
    </template>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MaterialPropertyTable from '../components/MaterialPropertyTable.vue'
import FlowStressChart from '../components/FlowStressChart.vue'
import { clearMaterialHistory, getFlowStressChart, getMaterial, listMaterials } from '../api/material'
import { useMaterialStore } from '../store/material'
const store = useMaterialStore()
const materials = ref([])
const selectedId = ref(store.currentMaterialId)
const material = ref(null)
const chart = ref({ x_axis: [], series: [] })
async function loadList() {
  const { data } = await listMaterials()
  materials.value = data.results || data
}
async function loadMaterial() {
  if (!selectedId.value) return
  const [matRes, chartRes] = await Promise.all([getMaterial(selectedId.value), getFlowStressChart(selectedId.value)])
  material.value = matRes.data
  chart.value = chartRes.data
  store.setCurrentMaterial(selectedId.value)
}
async function confirmClearHistory() {
  await ElMessageBox.confirm(
    '确认清空所有历史材料记录吗？该操作会清除下拉框中的历史材料，并删除已生成的导出记录。',
    '清空历史材料',
    { confirmButtonText: '确认清空', cancelButtonText: '取消', type: 'warning' }
  )
  const { data } = await clearMaterialHistory()
  materials.value = []
  selectedId.value = null
  material.value = null
  chart.value = { x_axis: [], series: [] }
  store.currentMaterialId = null
  localStorage.removeItem('currentMaterialId')
  ElMessage.success(`已清空 ${data.deleted_materials} 条历史材料记录`)
}
onMounted(async () => { await loadList(); await loadMaterial() })
</script>
