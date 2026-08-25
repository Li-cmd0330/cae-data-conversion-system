<template>
  <div class="algorithm-page">
    <el-card class="page-card">
      <div class="title-row">
        <div>
          <h1 class="page-title">材料算法分析</h1>
          <p class="subtitle">基于已解析 KEY 材料数据，进行流动应力预测、数据完整度评估、单位换算和本构参数估算。</p>
        </div>
        <el-button @click="loadMaterials">刷新材料</el-button>
      </div>

      <el-alert
        title="建议先上传 KEY 文件，再在本页面选择材料进行分析。算法结果用于前处理辅助判断，正式仿真前仍需结合材料实验数据校核。"
        type="info"
        show-icon
        :closable="false"
      />

      <div class="toolbar" style="margin-top: 18px">
        <el-select v-model="selectedId" placeholder="选择材料" filterable style="width: 360px" @change="loadMaterial">
          <el-option v-for="item in materials" :key="item.id" :label="item.name || item.file?.filename" :value="item.id" />
        </el-select>
        <el-tag v-if="material" type="success">{{ material.file?.filename }}</el-tag>
      </div>
    </el-card>

    <template v-if="material">
      <el-row :gutter="16" class="section-row">
        <el-col :span="8">
          <el-card class="metric-card">
            <div class="metric-label">材料名称</div>
            <div class="metric-value">{{ material.name || '未命名材料' }}</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="metric-card">
            <div class="metric-label">数据完整度</div>
            <div class="metric-value">{{ completeness?.score ?? '-' }}%</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="metric-card">
            <div class="metric-label">流动应力数据</div>
            <div class="metric-value">{{ hasFlowStress ? '已提供' : '未提供' }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="page-card section-row">
        <el-tabs>
          <el-tab-pane label="数据完整度评估">
            <el-row :gutter="16">
              <el-col :span="10">
                <el-progress type="dashboard" :percentage="completeness?.score || 0" />
              </el-col>
              <el-col :span="14">
                <el-descriptions border :column="1">
                  <el-descriptions-item label="已识别字段">{{ completeness?.present?.join(', ') || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="缺失字段">{{ completeness?.missing?.join(', ') || '无' }}</el-descriptions-item>
                </el-descriptions>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="流动应力预测">
            <template v-if="hasFlowStress">
              <div class="hint-box">根据 FSTRES 数据，对指定应变、温度和应变率进行插值预测。</div>
              <div class="toolbar form-toolbar">
                <el-input-number v-model="predictForm.strain" :step="0.01" :precision="4" />
                <span>应变</span>
                <el-input-number v-model="predictForm.temperature" :step="10" />
                <span>温度 °C</span>
                <el-input-number v-model="predictForm.strainRate" :step="1" />
                <span>应变率 /s</span>
                <el-select v-model="predictForm.method" style="width: 120px">
                  <el-option label="线性" value="linear" />
                  <el-option label="最近邻" value="nearest" />
                </el-select>
                <el-button type="primary" @click="runFlowStressPredict">预测</el-button>
              </div>
              <el-result v-if="predictResult !== null" title="预测流动应力" :sub-title="`${predictResult.toFixed(4)} MPa`" />
            </template>
            <el-empty v-else description="当前材料未包含 FSTRES 流动应力数据" />
          </el-tab-pane>

          <el-tab-pane label="Johnson-Cook 参数估算">
            <template v-if="firstStressCurve.length">
              <div class="hint-box">从当前材料第一组流动应力曲线中提取应变-应力数据，给出 Johnson-Cook 参数初始估算。</div>
              <el-button type="primary" @click="runFit">估算参数</el-button>
              <el-descriptions v-if="fitResult" border :column="3" style="margin-top: 16px">
                <el-descriptions-item label="A">{{ fitResult.A }}</el-descriptions-item>
                <el-descriptions-item label="B">{{ fitResult.B }}</el-descriptions-item>
                <el-descriptions-item label="n">{{ fitResult.n }}</el-descriptions-item>
                <el-descriptions-item label="C">{{ fitResult.C }}</el-descriptions-item>
                <el-descriptions-item label="m">{{ fitResult.m }}</el-descriptions-item>
                <el-descriptions-item label="说明">{{ fitResult.note }}</el-descriptions-item>
              </el-descriptions>
            </template>
            <el-empty v-else description="当前材料缺少可用于估算的流动应力曲线" />
          </el-tab-pane>

          <el-tab-pane label="工程单位换算">
            <div class="hint-box">用于前处理数据校核：应力、密度、温度等常见单位换算。</div>
            <div class="toolbar form-toolbar">
              <el-input-number v-model="unitForm.value" />
              <el-select v-model="unitForm.quantity" style="width: 130px" @change="resetUnits">
                <el-option label="应力" value="stress" />
                <el-option label="密度" value="density" />
                <el-option label="温度" value="temperature" />
              </el-select>
              <el-input v-model="unitForm.fromUnit" placeholder="from" style="width: 120px" />
              <span>→</span>
              <el-input v-model="unitForm.toUnit" placeholder="to" style="width: 120px" />
              <el-button type="primary" @click="runUnitConvert">换算</el-button>
            </div>
            <el-result v-if="unitResult !== null" title="换算结果" :sub-title="String(unitResult)" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </template>

    <el-card v-else class="page-card section-row">
      <el-empty description="请选择一个已上传材料进行算法分析" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { fitJohnsonCook, flowStressPredict, materialCompleteness, unitConvert } from '../api/algorithms'
import { getMaterial, listMaterials } from '../api/material'
import { useMaterialStore } from '../store/material'

const store = useMaterialStore()
const materials = ref([])
const selectedId = ref(store.currentMaterialId)
const material = ref(null)
const completeness = ref(null)
const predictResult = ref(null)
const fitResult = ref(null)
const unitResult = ref(null)
const predictForm = ref({ strain: 0.1, temperature: 20, strainRate: 1, method: 'linear' })
const unitForm = ref({ value: 1, quantity: 'stress', fromUnit: 'MPa', toUnit: 'Pa' })

const materialData = computed(() => material.value?.normalized_data || material.value?.raw_data || {})
const fstres = computed(() => materialData.value.FSTRES || null)
const hasFlowStress = computed(() => Boolean(fstres.value?.stress_data?.length))
const firstStressCurve = computed(() => {
  const stress = fstres.value?.stress_data || []
  if (!stress.length) return []
  const first = stress[0]
  return Array.isArray(first?.[0]) ? first[0] : first
})

async function loadMaterials() {
  const { data } = await listMaterials()
  materials.value = data.results || data
}
async function loadMaterial() {
  if (!selectedId.value) return
  const { data } = await getMaterial(selectedId.value)
  material.value = data
  store.setCurrentMaterial(selectedId.value)
  predictResult.value = null
  fitResult.value = null
  await runCompleteness()
}
async function runCompleteness() {
  const { data } = await materialCompleteness({ material_data: materialData.value })
  completeness.value = data
}
async function runFlowStressPredict() {
  const { data } = await flowStressPredict({
    fstres_data: fstres.value,
    strain: predictForm.value.strain,
    temperature: predictForm.value.temperature,
    strain_rate: predictForm.value.strainRate,
    method: predictForm.value.method
  })
  predictResult.value = data.stress
}
async function runFit() {
  const { data } = await fitJohnsonCook({
    strain: fstres.value?.strain_data || [],
    stress: firstStressCurve.value
  })
  fitResult.value = data
}
async function runUnitConvert() {
  const { data } = await unitConvert({
    value: unitForm.value.value,
    quantity: unitForm.value.quantity,
    from_unit: unitForm.value.fromUnit,
    to_unit: unitForm.value.toUnit
  })
  unitResult.value = data.value
}
function resetUnits() {
  const defaults = {
    stress: ['MPa', 'Pa'],
    density: ['kg/mm3', 'kg/m3'],
    temperature: ['C', 'K']
  }
  const [from, to] = defaults[unitForm.value.quantity]
  unitForm.value.fromUnit = from
  unitForm.value.toUnit = to
  unitResult.value = null
}

onMounted(async () => {
  await loadMaterials()
  await loadMaterial()
})
</script>

<style scoped>
.algorithm-page { display: grid; gap: 16px; }
.title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.subtitle { margin: -8px 0 18px; color: #64748b; }
.section-row { margin-top: 16px; }
.metric-card { border-radius: 14px; }
.metric-label { color: #64748b; font-size: 13px; margin-bottom: 8px; }
.metric-value { font-size: 22px; font-weight: 800; color: #0f172a; }
.hint-box { padding: 12px 14px; margin-bottom: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; color: #475569; }
.form-toolbar { flex-wrap: wrap; }
</style>
