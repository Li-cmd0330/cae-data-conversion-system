<template>
  <div v-if="classification && classification.confidence > 0.3" class="classification-panel">
    <el-alert 
      :title="`✨ 智能识别: ${classification.type_cn}`"
      type="success"
      :closable="false"
    >
      <div class="classification-content">
        <div class="classification-header">
          <span class="material-icon">{{ classification.icon }}</span>
          <div class="classification-info">
            <div class="classification-name">{{ classification.type_cn }}</div>
            <div class="classification-meta">
              <el-tag size="small" type="success">
                置信度: {{ (classification.confidence * 100).toFixed(0) }}%
              </el-tag>
              <span class="classification-method">{{ classification.method }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="classification.tags && classification.tags.length" class="classification-tags">
          <span class="tags-label">自动标签:</span>
          <el-tag 
            v-for="tag in classification.tags" 
            :key="tag"
            size="small"
            style="margin-right: 8px;"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <div v-if="similarMaterials && similarMaterials.length" class="similar-materials">
          <div class="similar-label">💡 相似材料推荐:</div>
          <div class="similar-list">
            <el-link 
              v-for="mat in similarMaterials"
              :key="mat.id"
              type="primary"
              @click="$emit('view-material', mat.id)"
              style="margin-right: 12px;"
            >
              {{ mat.name }}
            </el-link>
          </div>
        </div>
      </div>
    </el-alert>
  </div>
</template>

<script setup>
defineProps({
  classification: {
    type: Object,
    required: true
  },
  similarMaterials: {
    type: Array,
    default: () => []
  }
})

defineEmits(['view-material'])
</script>

<style scoped>
.classification-panel {
  margin: 16px 0;
}

.classification-content {
  padding: 8px 0;
}

.classification-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.material-icon {
  font-size: 48px;
}

.classification-info {
  flex: 1;
}

.classification-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.classification-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.classification-method {
  font-size: 13px;
  color: #909399;
}

.classification-tags {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-top: 1px dashed #e4e7ed;
}

.tags-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-right: 8px;
}

.similar-materials {
  padding-top: 12px;
  border-top: 1px dashed #e4e7ed;
}

.similar-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

.similar-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
