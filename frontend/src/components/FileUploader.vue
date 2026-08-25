<template>
  <el-upload drag multiple :auto-upload="false" :show-file-list="true" accept=".KEY,.key" :on-change="onChange" :on-remove="onRemove">
    <div class="upload-icon">KEY</div>
    <div>拖拽一个或多个 DEFORM .KEY 文件到此处，或点击选择文件</div>
    <template #tip><div class="el-upload__tip">后端解析后只保留结构化材料数据，不保留原始 KEY 文件</div></template>
  </el-upload>
</template>

<script setup>
const emit = defineEmits(['selected'])
let files = []
function onChange(uploadFile, uploadFiles) {
  files = uploadFiles.map(item => item.raw).filter(Boolean)
  emit('selected', files)
}
function onRemove(uploadFile, uploadFiles) {
  files = uploadFiles.map(item => item.raw).filter(Boolean)
  emit('selected', files)
}
</script>

<style scoped>
.upload-icon { font-size: 36px; font-weight: 900; color: #2563eb; margin-bottom: 12px; }
</style>
