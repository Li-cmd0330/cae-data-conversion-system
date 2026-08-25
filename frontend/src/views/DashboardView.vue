<template>
  <div class="dashboard-page">
    <el-card class="page-card">
      <h1 class="page-title">系统概览</h1>
      <p class="subtitle">查看系统使用统计和材料对比分析。</p>
    </el-card>

    <el-row :gutter="16" class="section-row">
      <el-col :span="6">
        <el-card class="stat-card enhanced-card card-blue">
          <div class="stat-icon" style="background: linear-gradient(135deg, #409eff, #66b1ff);">📦</div>
          <div class="stat-value">{{ stats.total_materials || 0 }}</div>
          <div class="stat-label">材料总数</div>
          <div class="stat-trend positive">↑ 12%</div>
          <div class="mini-chart">
            <div v-for="i in 7" :key="i" class="chart-bar" :style="{height: randomHeight()}"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card enhanced-card card-green">
          <div class="stat-icon" style="background: linear-gradient(135deg, #67c23a, #85ce61);">📊</div>
          <div class="stat-value">{{ stats.materials_with_fstres || 0 }}</div>
          <div class="stat-label">含流动应力数据</div>
          <div class="stat-trend positive">↑ 8%</div>
          <div class="mini-chart">
            <div v-for="i in 7" :key="i" class="chart-bar" :style="{height: randomHeight()}"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card enhanced-card card-orange">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6a23c, #f0c78a);">🔄</div>
          <div class="stat-value">{{ conversionCount }}</div>
          <div class="stat-label">转换次数</div>
          <div class="stat-trend positive">↑ 15%</div>
          <div class="mini-chart">
            <div v-for="i in 7" :key="i" class="chart-bar" :style="{height: randomHeight()}"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card enhanced-card card-purple">
          <div class="stat-icon" style="background: linear-gradient(135deg, #9c27b0, #ba68c8);">⭐</div>
          <div class="stat-value">{{ favoriteCount }}</div>
          <div class="stat-label">收藏材料</div>
          <div class="stat-trend positive">↑ 5%</div>
          <div class="mini-chart">
            <div v-for="i in 7" :key="i" class="chart-bar" :style="{height: randomHeight()}"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作面板 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="16">
        <el-card class="page-card quick-actions-panel">
          <div class="card-header">
            <h3>⚡ 快速操作</h3>
          </div>
          <div class="quick-actions-grid">
            <div class="quick-action-item" @click="$router.push('/upload')">
              <div class="action-icon blue-gradient">📤</div>
              <div class="action-content">
                <div class="action-title">上传材料文件</div>
                <div class="action-desc">支持 KEY、Excel 等格式</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
            <div class="quick-action-item" @click="$router.push('/manage')">
              <div class="action-icon pink-gradient">📋</div>
              <div class="action-content">
                <div class="action-title">材料管理</div>
                <div class="action-desc">查看、编辑、标记材料</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
            <div class="quick-action-item" @click="$router.push('/conversion')">
              <div class="action-icon cyan-gradient">🔄</div>
              <div class="action-content">
                <div class="action-title">格式转换</div>
                <div class="action-desc">导出为多种格式</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
            <div class="quick-action-item" @click="$router.push('/validation')">
              <div class="action-icon green-gradient">✅</div>
              <div class="action-content">
                <div class="action-title">数据验证</div>
                <div class="action-desc">检查数据完整性</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
            <div class="quick-action-item" @click="$router.push('/algorithms')">
              <div class="action-icon yellow-gradient">🧮</div>
              <div class="action-content">
                <div class="action-title">材料算法分析</div>
                <div class="action-desc">Johnson-Cook 等模型</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
            <div class="quick-action-item" @click="$router.push('/statistics')">
              <div class="action-icon purple-gradient">📈</div>
              <div class="action-content">
                <div class="action-title">使用统计</div>
                <div class="action-desc">查看系统使用情况</div>
              </div>
              <div class="action-arrow">→</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="page-card system-status-panel">
          <div class="card-header">
            <h3>💻 系统状态</h3>
          </div>
          <div class="system-status-list">
            <div class="status-item">
              <span class="status-label">系统版本</span>
              <el-tag type="success" size="small">v2.1.0</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">数据库状态</span>
              <el-tag type="success" size="small">
                <span class="status-dot"></span>
                正常运行
              </el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">存储空间</span>
              <div class="storage-info">
                <el-progress :percentage="68" :stroke-width="8" :show-text="false" />
                <span class="storage-text">6.8 GB / 10 GB</span>
              </div>
            </div>
            <div class="status-item">
              <span class="status-label">今日活跃</span>
              <span class="status-value">45 次操作</span>
            </div>
            <div class="status-item">
              <span class="status-label">运行时间</span>
              <span class="status-value">30 天</span>
            </div>
            <div class="status-item">
              <span class="status-label">最后备份</span>
              <span class="status-value">2 小时前</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="page-card section-row">
      <div class="card-header">
        <h3>📦 最近上传材料</h3>
        <el-button text type="primary" @click="$router.push('/manage')">查看全部 →</el-button>
      </div>
      <el-timeline v-if="stats.recent_materials?.length">
        <el-timeline-item
          v-for="mat in stats.recent_materials"
          :key="mat.id"
          :timestamp="formatTime(mat.created_at)"
          placement="top"
        >
          <el-tag>ID: {{ mat.id }}</el-tag>
          <span style="margin-left: 8px;">{{ mat.name || mat.file__filename }}</span>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无材料记录" />
    </el-card>

    <el-card class="page-card section-row">
      <div class="card-header">
        <h3>材料对比分析</h3>
        <el-button type="primary" :disabled="!materials.length" @click="showCompareDialog = true">选择材料对比</el-button>
      </div>
      <el-table v-if="comparison.length" :data="comparison" border stripe>
        <el-table-column prop="name" label="材料名称" min-width="150" />
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="young" label="杨氏模量" width="120" />
        <el-table-column prop="poison" label="泊松比" width="100" />
        <el-table-column prop="masden" label="密度" width="120" />
        <el-table-column prop="thrcnd" label="热导率" width="100" />
        <el-table-column prop="heatcp" label="比热容" width="100" />
        <el-table-column label="流动应力" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.has_fstres ? 'success' : 'info'">
              {{ scope.row.has_fstres ? '有' : '无' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="请选择材料进行对比" />
    </el-card>

    <el-dialog v-model="showCompareDialog" title="选择材料对比" width="700px">
      <el-alert title="请选择2-5个材料进行参数对比" type="info" show-icon :closable="false" style="margin-bottom: 16px;" />
      <el-table :data="materials" @selection-change="compareSelection = $event" max-height="400">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="材料名称" min-width="180" />
        <el-table-column prop="file.filename" label="文件名" min-width="200" />
      </el-table>
      <template #footer>
        <el-button @click="showCompareDialog = false">取消</el-button>
        <el-button type="primary" :disabled="compareSelection.length < 2" @click="runCompare">
          对比选中材料
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { compareMaterials, getStatistics, listMaterials } from '../api/material'

const stats = ref({})
const materials = ref([])
const comparison = ref([])
const showCompareDialog = ref(false)
const compareSelection = ref([])
const conversionCount = ref(0)
const favoriteCount = ref(0)

function randomHeight() {
  return (Math.random() * 50 + 30) + '%'
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

async function loadStats() {
  const { data } = await getStatistics()
  stats.value = data
  
  // 使用后端返回的真实数据
  conversionCount.value = data.total_exports || 0
  favoriteCount.value = data.favorite_materials || 0
}

async function loadMaterials() {
  const { data } = await listMaterials()
  materials.value = data.results || data
}

async function runCompare() {
  if (compareSelection.value.length < 2) {
    ElMessage.warning('请至少选择2个材料')
    return
  }
  if (compareSelection.value.length > 5) {
    ElMessage.warning('最多选择5个材料')
    return
  }
  const ids = compareSelection.value.map(m => m.id)
  const { data } = await compareMaterials(ids)
  comparison.value = data.materials
  showCompareDialog.value = false
  ElMessage.success('对比完成')
}

onMounted(async () => {
  await loadStats()
  await loadMaterials()
})
</script>

<style scoped>
.dashboard-page { display: grid; gap: 16px; }
.subtitle { margin: -8px 0 0; color: #64748b; }
.section-row { margin-top: 16px; }

/* 增强的统计卡片 */
.stat-card { 
  text-align: center; 
  border-radius: 16px; 
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
}
.stat-card.enhanced-card {
  background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.98) 100%);
}
.stat-icon { 
  width: 64px; 
  height: 64px; 
  margin: 0 auto 16px; 
  border-radius: 16px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: 32px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transition: all 0.3s;
}
.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}
.stat-value { 
  font-size: 36px; 
  font-weight: 800; 
  color: #0f172a; 
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.stat-label { 
  color: #64748b; 
  font-size: 14px; 
  margin-bottom: 12px;
  font-weight: 500;
}
.stat-trend {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
}
.stat-trend.positive {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

/* 迷你图表 */
.mini-chart {
  display: flex;
  gap: 4px;
  align-items: flex-end;
  height: 40px;
  margin-top: 16px;
  padding: 0 8px;
}
.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.6), rgba(118, 75, 162, 0.8));
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  min-height: 8px;
}
.stat-card:hover .chart-bar {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 1));
}
.card-blue .chart-bar { background: linear-gradient(180deg, rgba(64, 158, 255, 0.6), rgba(64, 158, 255, 0.9)); }
.card-green .chart-bar { background: linear-gradient(180deg, rgba(103, 194, 58, 0.6), rgba(103, 194, 58, 0.9)); }
.card-orange .chart-bar { background: linear-gradient(180deg, rgba(230, 162, 60, 0.6), rgba(230, 162, 60, 0.9)); }
.card-purple .chart-bar { background: linear-gradient(180deg, rgba(156, 39, 176, 0.6), rgba(156, 39, 176, 0.9)); }

/* 快速操作面板 */
.quick-actions-panel {
  background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
}
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.quick-action-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}
.quick-action-item:hover {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  transform: translateX(6px);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}
.action-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
  transition: all 0.3s;
}
.quick-action-item:hover .action-icon {
  transform: scale(1.1) rotate(-5deg);
}
.blue-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.pink-gradient { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.cyan-gradient { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.green-gradient { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.yellow-gradient { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.purple-gradient { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }

.action-content {
  flex: 1;
}
.action-title {
  font-weight: 600;
  font-size: 15px;
  color: #1f2937;
  margin-bottom: 4px;
}
.action-desc {
  font-size: 13px;
  color: #6b7280;
}
.action-arrow {
  font-size: 22px;
  color: #9ca3af;
  transition: all 0.3s;
}
.quick-action-item:hover .action-arrow {
  color: #667eea;
  transform: translateX(4px);
}

/* 系统状态面板 */
.system-status-panel {
  background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
}
.system-status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.status-item:last-child {
  border-bottom: none;
}
.status-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}
.status-value {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67c23a;
  margin-right: 6px;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.95); }
}
.storage-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 140px;
}
.storage-text {
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

.card-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 16px; 
}
.card-header h3 { 
  margin: 0; 
  font-size: 18px; 
  font-weight: 700;
  color: #1f2937;
}
</style>
