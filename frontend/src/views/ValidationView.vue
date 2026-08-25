<template>
  <div class="validation-page">
    <el-card class="page-card">
      <div class="title-row">
        <div>
          <h1 class="page-title">数据验证报告</h1>
          <p class="subtitle">对已解析材料数据进行完整性、一致性和物理合理性验证，确保数据质量满足仿真前处理要求。</p>
        </div>
        <el-button @click="loadMaterials">刷新材料</el-button>
      </div>

      <el-alert
        title="验证规则包括：必需字段检查、推荐字段检查、数值范围检查、流动应力矩阵完整性、温度应变单调性和物理一致性。"
        type="info"
        show-icon
        :closable="false"
      />

      <div class="toolbar" style="margin-top: 18px">
        <el-select v-model="selectedId" placeholder="选择材料" filterable style="width: 360px" @change="loadValidation">
          <el-option v-for="item in materials" :key="item.id" :label="item.name || item.file?.filename" :value="item.id" />
        </el-select>
        <el-button type="primary" :disabled="!selectedId" :loading="validating" @click="runValidate">重新验证</el-button>
        <el-button :disabled="!materials.length" @click="showBatchDialog = true">批量验证</el-button>
      </div>
    </el-card>

    <template v-if="material && report">
      <el-row :gutter="16" class="section-row">
        <el-col :span="6">
          <el-card class="metric-card" :class="{ 'metric-valid': report.is_valid, 'metric-invalid': !report.is_valid }">
            <div class="metric-label">验证状态</div>
            <div class="metric-value">{{ report.is_valid ? '通过' : '未通过' }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card metric-error">
            <div class="metric-label">错误</div>
            <div class="metric-value">{{ report.errors?.length || 0 }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card metric-warning">
            <div class="metric-label">警告</div>
            <div class="metric-value">{{ report.warnings?.length || 0 }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="metric-card metric-info">
            <div class="metric-label">提示</div>
            <div class="metric-value">{{ report.info?.length || 0 }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="page-card section-row">
        <el-tabs>
          <el-tab-pane :label="`错误 (${report.errors?.length || 0})`">
            <el-empty v-if="!report.errors?.length" description="无错误" />
            <div v-else class="message-list">
              <el-alert v-for="(msg, idx) in report.errors" :key="idx" type="error" :title="msg" show-icon :closable="false" />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="`警告 (${report.warnings?.length || 0})`">
            <el-empty v-if="!report.warnings?.length" description="无警告" />
            <div v-else class="message-list">
              <el-alert v-for="(msg, idx) in report.warnings" :key="idx" type="warning" :title="msg" show-icon :closable="false" />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="`提示 (${report.info?.length || 0})`">
            <el-empty v-if="!report.info?.length" description="无提示信息" />
            <div v-else class="message-list">
              <el-alert v-for="(msg, idx) in report.info" :key="idx" type="info" :title="msg" show-icon :closable="false" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="数据质量评分">
            <el-row :gutter="16">
              <el-col :span="10">
                <el-progress type="dashboard" :percentage="qualityScore" :color="qualityColor" />
                <div style="text-align: center; margin-top: 16px; font-size: 14px; color: #64748b;">
                  综合质量评分
                </div>
              </el-col>
              <el-col :span="14">
                <el-descriptions border :column="1">
                  <el-descriptions-item label="材料名称">{{ material.name || '未命名' }}</el-descriptions-item>
                  <el-descriptions-item label="源文件">{{ material.file?.filename }}</el-descriptions-item>
                  <el-descriptions-item label="验证时间">{{ formatTime(report.created_at) }}</el-descriptions-item>
                  <el-descriptions-item label="错误数">{{ report.errors?.length || 0 }}</el-descriptions-item>
                  <el-descriptions-item label="警告数">{{ report.warnings?.length || 0 }}</el-descriptions-item>
                  <el-descriptions-item label="建议">{{ qualityAdvice }}</el-descriptions-item>
                </el-descriptions>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="验证历史">
            <el-table :data="validationHistory" border stripe>
              <el-table-column prop="created_at" label="验证时间" width="180">
                <template #default="scope">{{ formatTime(scope.row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.is_valid ? 'success' : 'danger'">
                    {{ scope.row.is_valid ? '通过' : '未通过' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="errors" label="错误" width="80">
                <template #default="scope">{{ scope.row.errors?.length || 0 }}</template>
              </el-table-column>
              <el-table-column prop="warnings" label="警告" width="80">
                <template #default="scope">{{ scope.row.warnings?.length || 0 }}</template>
              </el-table-column>
              <el-table-column prop="info" label="提示" width="80">
                <template #default="scope">{{ scope.row.info?.length || 0 }}</template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button link type="primary" @click="loadHistoryReport(scope.row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </template>

    <el-card v-else class="page-card section-row">
      <el-empty description="请选择一个材料查看验证报告" />
    </el-card>

    <el-dialog v-model="showBatchDialog" title="批量验证材料" width="600px">
      <el-table :data="materials" @selection-change="batchSelection = $event" max-height="400">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="材料名称" min-width="180" />
        <el-table-column prop="file.filename" label="文件名" min-width="200" />
      </el-table>
      <template #footer>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button type="primary" :disabled="!batchSelection.length" :loading="batchValidating" @click="runBatchValidate">
          验证选中材料
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getMaterial, listMaterials, validateMaterial } from '../api/material'
import { useMaterialStore } from '../store/material'

const store = useMaterialStore()
const materials = ref([])
const selectedId = ref(store.currentMaterialId)
const material = ref(null)
const report = ref(null)
const validationHistory = ref([])
const validating = ref(false)
const showBatchDialog = ref(false)
const batchSelection = ref([])
const batchValidating = ref(false)

const qualityScore = computed(() => {
  if (!report.value) return 0
  const errors = report.value.errors?.length || 0
  const warnings = report.value.warnings?.length || 0
  let score = 100
  score -= errors * 15
  score -= warnings * 5
  return Math.max(0, Math.min(100, score))
})

const qualityColor = computed(() => {
  const score = qualityScore.value
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
})

const qualityAdvice = computed(() => {
  const score = qualityScore.value
  if (score >= 90) return '数据质量优秀，可直接用于仿真'
  if (score >= 70) return '数据质量良好，建议修复警告项'
  if (score >= 50) return '数据质量一般，需修复错误和警告'
  return '数据质量较差，建议重新检查源文件'
})

async function loadMaterials() {
  const { data } = await listMaterials()
  materials.value = data.results || data
}

async function loadValidation() {
  if (!selectedId.value) return
  const { data } = await getMaterial(selectedId.value)
  material.value = data
  store.setCurrentMaterial(selectedId.value)
  validationHistory.value = data.latest_validation ? [data.latest_validation] : []
  report.value = data.latest_validation
}

async function runValidate() {
  validating.value = true
  try {
    const { data } = await validateMaterial(selectedId.value)
    report.value = data
    validationHistory.value.unshift(data)
    ElMessage.success('验证完成')
  } finally {
    validating.value = false
  }
}

async function runBatchValidate() {
  batchValidating.value = true
  try {
    let successCount = 0
    for (const mat of batchSelection.value) {
      await validateMaterial(mat.id)
      successCount++
    }
    ElMessage.success(`已完成 ${successCount} 个材料的验证`)
    showBatchDialog.value = false
    await loadValidation()
  } finally {
    batchValidating.value = false
  }
}

function loadHistoryReport(historyReport) {
  report.value = historyReport
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(async () => {
  await loadMaterials()
  await loadValidation()
})
</script>

<style scoped>
.validation-page { display: grid; gap: 16px; }
.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.subtitle { margin: -8px 0 18px; color: #64748b; }
.section-row { margin-top: 16px; }
.metric-card { border-radius: 14px; transition: all 0.3s; }
.metric-label { color: #64748b; font-size: 13px; margin-bottom: 8px; }
.metric-value { font-size: 22px; font-weight: 800; color: #0f172a; }
.metric-valid { border: 2px solid #67c23a; }
.metric-valid .metric-value { color: #67c23a; }
.metric-invalid { border: 2px solid #f56c6c; }
.metric-invalid .metric-value { color: #f56c6c; }
.metric-error .metric-value { color: #f56c6c; }
.metric-warning .metric-value { color: #e6a23c; }
.metric-info .metric-value { color: #409eff; }
.message-list { display: grid; gap: 10px; }
</style>
