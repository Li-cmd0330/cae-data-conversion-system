<template>
  <div class="materials-page">
    <el-card class="page-card">
      <div class="title-row">
        <div>
          <h1 class="page-title">材料管理</h1>
          <p class="subtitle">搜索、筛选、标记和管理所有已上传的材料数据。</p>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="$router.push('/upload')">上传新材料</el-button>
          <el-button @click="loadMaterials">刷新</el-button>
        </div>
      </div>

      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索材料名称、文件名或备注..."
          clearable
          style="width: 300px;"
          @input="handleSearch"
        >
          <template #prefix><span>🔍</span></template>
        </el-input>
        <el-input
          v-model="tagFilter"
          placeholder="按标签筛选..."
          clearable
          style="width: 200px;"
          @input="handleSearch"
        >
          <template #prefix><span>🏷️</span></template>
        </el-input>
        <el-select v-model="favoriteFilter" placeholder="收藏筛选" style="width: 140px;" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="仅收藏" value="true" />
        </el-select>
        <el-select v-model="fstresFilter" placeholder="流动应力" style="width: 160px;" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="含流动应力" value="true" />
        </el-select>
        <el-tag v-if="filteredCount < totalCount" type="info">
          筛选结果: {{ filteredCount }} / {{ totalCount }}
        </el-tag>
      </div>
    </el-card>

    <el-card class="page-card section-row">
      <div class="table-toolbar">
        <el-button :disabled="!selection.length" @click="batchAddTags">批量添加标签</el-button>
        <el-button :disabled="!selection.length" @click="batchToggleFavorite">批量收藏/取消</el-button>
        <el-button type="danger" plain :disabled="!selection.length" @click="batchDelete">批量删除</el-button>
        <span v-if="selection.length" style="margin-left: auto; color: #64748b;">
          已选择 {{ selection.length }} 个材料
        </span>
      </div>

      <el-table :data="materials" border stripe @selection-change="selection = $event" max-height="600">
        <el-table-column type="selection" width="55" />
        <el-table-column label="收藏" width="80" align="center">
          <template #default="scope">
            <el-button
              link
              :type="scope.row.is_favorite ? 'warning' : 'info'"
              @click="toggleFavorite(scope.row)"
            >
              {{ scope.row.is_favorite ? '⭐' : '☆' }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column type="index" label="序号" width="80" :index="(index) => index + 1" />
        <el-table-column prop="name" label="材料名称" min-width="180">
          <template #default="scope">
            <el-link type="primary" @click="viewDetail(scope.row.id)">
              {{ scope.row.name || '未命名' }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="file.filename" label="文件名" min-width="220" />
        <el-table-column label="标签" min-width="200">
          <template #default="scope">
            <el-tag
              v-for="tag in parseTags(scope.row.tags)"
              :key="tag"
              size="small"
              style="margin-right: 4px;"
            >
              {{ tag }}
            </el-tag>
            <el-button link size="small" @click="editTags(scope.row)">编辑</el-button>
          </template>
        </el-table-column>
        <el-table-column label="流动应力" width="100" align="center">
          <template #default="scope">
            <el-tag :type="hasFstres(scope.row) ? 'success' : 'info'" size="small">
              {{ hasFstres(scope.row) ? '有' : '无' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="scope">{{ formatTime(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="viewDetail(scope.row.id)">详情</el-button>
            <el-button link @click="editNotes(scope.row)">备注</el-button>
            <el-button link type="danger" @click="deleteMaterial(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showTagDialog" title="编辑标签" width="500px">
      <el-alert title="多个标签用逗号分隔，例如：铝合金,高温,锻造" type="info" show-icon :closable="false" style="margin-bottom: 16px;" />
      <el-input v-model="editingTags" placeholder="输入标签，用逗号分隔" />
      <div style="margin-top: 16px;">
        <div style="margin-bottom: 8px; color: #64748b; font-size: 13px;">常用标签：</div>
        <el-tag
          v-for="tag in popularTags"
          :key="tag"
          style="margin-right: 8px; margin-bottom: 8px; cursor: pointer;"
          @click="addPopularTag(tag)"
        >
          {{ tag }}
        </el-tag>
      </div>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTags">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showNoteDialog" title="编辑备注" width="600px">
      <el-input v-model="editingNotes" type="textarea" :rows="6" placeholder="输入材料备注信息..." />
      <template #footer>
        <el-button @click="showNoteDialog = false">取消</el-button>
        <el-button type="primary" @click="saveNotes">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { http } from '../api/http'
import { getStatistics } from '../api/material'

const router = useRouter()
const materials = ref([])
const selection = ref([])
const searchText = ref('')
const tagFilter = ref('')
const favoriteFilter = ref('')
const fstresFilter = ref('')
const totalCount = ref(0)
const filteredCount = ref(0)
const popularTags = ref([])
const showTagDialog = ref(false)
const showNoteDialog = ref(false)
const editingMaterial = ref(null)
const editingTags = ref('')
const editingNotes = ref('')

function parseTags(tags) {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

function hasFstres(material) {
  const data = material.normalized_data || material.raw_data || {}
  return Boolean(data.FSTRES)
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

async function loadMaterials() {
  const params = {}
  if (searchText.value) params.search = searchText.value
  if (tagFilter.value) params.tags = tagFilter.value
  if (favoriteFilter.value) params.is_favorite = favoriteFilter.value
  if (fstresFilter.value) params.has_fstres = fstresFilter.value
  
  const { data } = await http.get('/materials/', { params })
  materials.value = data.results || data
  filteredCount.value = materials.value.length
}

async function loadStats() {
  const { data } = await getStatistics()
  totalCount.value = data.total_materials
  popularTags.value = data.popular_tags?.map(item => item[0]) || []
}

function handleSearch() {
  loadMaterials()
}

function viewDetail(id) {
  router.push(`/materials?id=${id}`)
}

async function toggleFavorite(material) {
  await http.post(`/materials/${material.id}/toggle-favorite/`)
  material.is_favorite = !material.is_favorite
  ElMessage.success(material.is_favorite ? '已添加到收藏' : '已取消收藏')
}

function editTags(material) {
  editingMaterial.value = material
  editingTags.value = material.tags || ''
  showTagDialog.value = true
}

function editNotes(material) {
  editingMaterial.value = material
  editingNotes.value = material.notes || ''
  showNoteDialog.value = true
}

function addPopularTag(tag) {
  const current = editingTags.value.split(',').map(t => t.trim()).filter(Boolean)
  if (!current.includes(tag)) {
    current.push(tag)
    editingTags.value = current.join(', ')
  }
}

async function saveTags() {
  await http.patch(`/materials/${editingMaterial.value.id}/`, { tags: editingTags.value })
  editingMaterial.value.tags = editingTags.value
  showTagDialog.value = false
  ElMessage.success('标签已保存')
}

async function saveNotes() {
  await http.patch(`/materials/${editingMaterial.value.id}/`, { notes: editingNotes.value })
  editingMaterial.value.notes = editingNotes.value
  showNoteDialog.value = false
  ElMessage.success('备注已保存')
}

async function batchAddTags() {
  const { value } = await ElMessageBox.prompt('输入要添加的标签（逗号分隔）', '批量添加标签')
  for (const mat of selection.value) {
    const current = parseTags(mat.tags)
    const newTags = value.split(',').map(t => t.trim()).filter(Boolean)
    const merged = [...new Set([...current, ...newTags])]
    await http.patch(`/materials/${mat.id}/`, { tags: merged.join(', ') })
    mat.tags = merged.join(', ')
  }
  ElMessage.success(`已为 ${selection.value.length} 个材料添加标签`)
}

async function batchToggleFavorite() {
  for (const mat of selection.value) {
    await http.post(`/materials/${mat.id}/toggle-favorite/`)
    mat.is_favorite = !mat.is_favorite
  }
  ElMessage.success(`已更新 ${selection.value.length} 个材料的收藏状态`)
}

async function deleteMaterial(material) {
  await ElMessageBox.confirm('确认删除该材料吗？', '删除材料', { type: 'warning' })
  await http.delete(`/materials/${material.id}/`)
  await loadMaterials()
  ElMessage.success('材料已删除')
}

async function batchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selection.value.length} 个材料吗？`, '批量删除', { type: 'warning' })
  for (const mat of selection.value) {
    await http.delete(`/materials/${mat.id}/`)
  }
  await loadMaterials()
  ElMessage.success(`已删除 ${selection.value.length} 个材料`)
}

onMounted(async () => {
  await loadStats()
  await loadMaterials()
})
</script>

<style scoped>
.materials-page { display: grid; gap: 16px; }
.title-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.subtitle { margin: -8px 0 0; color: #64748b; }
.action-buttons { display: flex; gap: 8px; }
.section-row { margin-top: 16px; }
.filter-bar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-top: 16px; }
.table-toolbar { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; }
</style>
