<template>
  <el-card class="page-card">
    <h1 class="page-title">文件上传与解析</h1>
    <FileUploader @selected="files = $event" />
    <div class="toolbar" style="margin-top: 18px">
      <el-button type="primary" :disabled="!files.length" :loading="loading" @click="submit">
        上传并解析
      </el-button>
      <span v-if="files.length">已选择 {{ files.length }} 个 KEY 文件</span>
      <el-tag v-if="loading" type="warning" style="margin-left: 12px;">
        正在处理 {{ uploadProgress.current }} / {{ uploadProgress.total }}
      </el-tag>
    </div>
    <el-alert 
      title="上传后的原始 KEY 文件会在解析完成后自动从系统中删除，仅保留材料结构化数据用于后续导出。" 
      type="info" 
      show-icon 
      :closable="false" 
    />
    <el-divider />

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon closable @close="errorMessage = ''" style="margin-bottom: 16px;" />

    <!-- 智能识别结果 -->
    <MaterialClassification 
      v-if="results.length && results[0].classification"
      :classification="results[0].classification"
      :similar-materials="results[0].similar_materials"
      @view-material="viewDetail"
    />

    <!-- 智能数据修复 -->
    <DataRepairPanel
      v-if="results.length && results[0].repair_analysis"
      :repair-analysis="results[0].repair_analysis"
      @apply-fix="handleApplyFix"
      @ignore="handleIgnoreRepair"
    />

    <el-table v-if="results.length" :data="results" border stripe>
      <el-table-column prop="material_id" label="材料ID" width="90" />
      <el-table-column prop="filename" label="源文件名" min-width="220" />
      <el-table-column prop="material_name" label="材料名称" min-width="180" />
      <el-table-column label="KEY文件保留" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.source_file_retained ? 'warning' : 'success'">
            {{ scope.row.source_file_retained ? '已保留' : '未保留' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="验证状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.validation?.is_valid ? 'success' : 'danger'">
            {{ scope.row.validation?.is_valid ? '通过' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button link type="primary" @click="viewDetail(scope.row.material_id)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <template v-if="results.length">
      <el-divider />
      <el-tabs>
        <el-tab-pane v-for="(result, idx) in results" :key="idx" :label="`${result.material_name || result.filename} (ID: ${result.material_id})`">
          <ValidationReport :report="result.validation" />
          <el-divider />
          <div style="margin-bottom: 8px; font-weight: 600;">解析数据预览：</div>
          <el-input type="textarea" :rows="10" :model-value="JSON.stringify(result.parsed_data, null, 2)" readonly />
        </el-tab-pane>
      </el-tabs>
    </template>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import FileUploader from '../components/FileUploader.vue'
import ValidationReport from '../components/ValidationReport.vue'
import MaterialClassification from '../components/MaterialClassification.vue'
import DataRepairPanel from '../components/DataRepairPanel.vue'
import { uploadMaterial, uploadMaterials } from '../api/material'
import { useMaterialStore } from '../store/material'

const router = useRouter()
const store = useMaterialStore()
const files = ref([])
const loading = ref(false)
const results = ref([])
const errorMessage = ref('')
const uploadProgress = ref({ current: 0, total: 0 })

function handleApplyFix(fixableParams) {
  ElMessage.success(`已应用 ${fixableParams.length} 个自动修复`)
  // TODO: 调用API应用修复
}

function handleIgnoreRepair() {
  ElMessage.info('已忽略修复建议')
}

async function submit() {
  if (!files.value.length) {
    ElMessage.warning('请先选择文件')
    return
  }

  loading.value = true
  errorMessage.value = ''
  results.value = []
  uploadProgress.value = { current: 0, total: files.value.length }

  try {
    if (files.value.length === 1) {
      // 单文件上传
      uploadProgress.value.current = 1
      const { data } = await uploadMaterial(files.value[0])
      results.value = [data]
      if (data) store.setUploadResult(data)
      ElMessage.success('文件上传并解析成功')
    } else {
      // 批量上传
      const { data } = await uploadMaterials(files.value)
      uploadProgress.value.current = files.value.length
      results.value = data.results || []
      if (results.value[0]) store.setUploadResult(results.value[0])
      ElMessage.success(`成功上传并解析 ${results.value.length} 个文件`)
    }
  } catch (error) {
    console.error('Upload error:', error)
    const errorMsg = error.response?.data?.detail || error.message || '上传失败，请检查文件格式'
    errorMessage.value = errorMsg
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
    uploadProgress.value = { current: 0, total: 0 }
  }
}

function viewDetail(materialId) {
  router.push(`/materials?id=${materialId}`)
}
</script>
