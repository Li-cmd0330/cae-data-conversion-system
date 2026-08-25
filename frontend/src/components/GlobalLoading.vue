<template>
  <div v-if="visible" class="global-loading">
    <div class="loading-backdrop" @click="handleBackdropClick"></div>
    <div class="loading-content">
      <div class="loading-spinner">
        <div class="spinner"></div>
      </div>
      <div class="loading-text">{{ text }}</div>
      <div v-if="tip" class="loading-tip">{{ tip }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const text = ref('加载中...')
const tip = ref('')
const closable = ref(false)

function show(options = {}) {
  text.value = options.text || '加载中...'
  tip.value = options.tip || ''
  closable.value = options.closable || false
  visible.value = true
}

function hide() {
  visible.value = false
  text.value = '加载中...'
  tip.value = ''
}

function handleBackdropClick() {
  if (closable.value) {
    hide()
  }
}

defineExpose({ show, hide })
</script>

<style scoped>
.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.loading-content {
  position: relative;
  background: white;
  border-radius: 16px;
  padding: 40px 60px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  text-align: center;
  min-width: 200px;
}

.loading-spinner {
  margin-bottom: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.loading-tip {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}
</style>
