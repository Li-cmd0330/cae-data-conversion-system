<template>
  <div v-if="repairAnalysis && repairAnalysis.has_issues" class="repair-panel">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔧 智能数据修复</span>
          <el-tag :type="getSeverityType()">
            发现 {{ repairAnalysis.total_issues }} 个问题
          </el-tag>
        </div>
      </template>
      
      <!-- 问题列表 -->
      <el-collapse v-model="activeNames" accordion>
        <el-collapse-item 
          v-for="(issue, index) in repairAnalysis.issues" 
          :key="index"
          :name="index"
        >
          <template #title>
            <div class="issue-title">
              <el-icon :color="getSeverityColor(issue.severity)" style="margin-right: 8px;">
                <Warning v-if="issue.severity === 'high'" />
                <InfoFilled v-else />
              </el-icon>
              <span>{{ issue.message }}</span>
            </div>
          </template>
          
          <div class="issue-detail">
            <div class="issue-info">
              <span class="label">参数:</span>
              <el-tag size="small">{{ issue.parameter }}</el-tag>
            </div>
            
            <div v-if="issue.current_value !== undefined" class="issue-info">
              <span class="label">当前值:</span>
              <span class="value">{{ formatValue(issue.current_value) }}</span>
            </div>
            
            <div v-if="issue.expected_range" class="issue-info">
              <span class="label">正常范围:</span>
              <span class="value">
                [{{ formatValue(issue.expected_range[0]) }}, {{ formatValue(issue.expected_range[1]) }}]
              </span>
            </div>
            
            <div v-if="repairAnalysis.suggestions[issue.parameter]" class="suggestion">
              <span class="label">💡 建议值:</span>
              <span class="value suggested">
                {{ formatValue(repairAnalysis.suggestions[issue.parameter]) }}
              </span>
              <el-tag size="small" type="success" style="margin-left: 8px;">
                置信度: {{ (repairAnalysis.confidence[issue.parameter] * 100).toFixed(0) }}%
              </el-tag>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <el-button 
          type="primary" 
          :disabled="!repairAnalysis.auto_fixable || !repairAnalysis.auto_fixable.length"
          @click="handleAutoFix"
        >
          自动修复 ({{ repairAnalysis.auto_fixable ? repairAnalysis.auto_fixable.length : 0 }}个)
        </el-button>
        <el-button @click="$emit('ignore')">
          忽略问题
        </el-button>
      </div>
    </el-card>
  </div>
  
  <!-- 无问题提示 -->
  <el-alert 
    v-else-if="repairAnalysis && !repairAnalysis.has_issues"
    title="✅ 数据质量良好"
    type="success"
    :closable="false"
    show-icon
    style="margin: 16px 0;"
  >
    未发现数据问题，可以直接使用
  </el-alert>
</template>

<script setup>
import { ref } from 'vue'
import { Warning, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  repairAnalysis: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['apply-fix', 'ignore'])

const activeNames = ref([0])

function getSeverityType() {
  if (!props.repairAnalysis) return 'info'
  if (props.repairAnalysis.critical_issues > 0) return 'danger'
  return 'warning'
}

function getSeverityColor(severity) {
  const colors = {
    high: '#f56c6c',
    medium: '#e6a23c',
    low: '#909399'
  }
  return colors[severity] || '#909399'
}

function formatValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    if (value < 0.01 && value > 0) {
      return value.toExponential(2)
    }
    return value.toFixed(2)
  }
  return value
}

function handleAutoFix() {
  emit('apply-fix', props.repairAnalysis.auto_fixable)
}
</script>

<style scoped>
.repair-panel {
  margin: 16px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.issue-title {
  display: flex;
  align-items: center;
  width: 100%;
}

.issue-detail {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.issue-info {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.value {
  color: #303133;
}

.value.suggested {
  color: #67c23a;
  font-weight: 600;
  font-size: 15px;
}

.suggestion {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #dcdfe6;
  display: flex;
  align-items: center;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}
</style>
