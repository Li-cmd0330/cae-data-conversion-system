<template>
  <div class="statistics-page">
    <el-card class="page-card">
      <h1 class="page-title">使用统计仪表板</h1>
      <p class="subtitle">查看系统使用情况、数据趋势和操作统计，全面了解系统运行状态。</p>
    </el-card>

    <!-- 核心统计指标 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e3f2fd;">📦</div>
          <div class="stat-value">{{ stats.total_materials || 0 }}</div>
          <div class="stat-label">材料总数</div>
          <div class="stat-trend" :class="getTrendClass(stats.material_trend)">
            {{ getTrendText(stats.material_trend) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f3e5f5;">📊</div>
          <div class="stat-value">{{ stats.total_uploads || 0 }}</div>
          <div class="stat-label">上传次数</div>
          <div class="stat-trend" :class="getTrendClass(stats.upload_trend)">
            {{ getTrendText(stats.upload_trend) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e8f5e9;">🔄</div>
          <div class="stat-value">{{ stats.total_conversions || 0 }}</div>
          <div class="stat-label">转换次数</div>
          <div class="stat-trend" :class="getTrendClass(stats.conversion_trend)">
            {{ getTrendText(stats.conversion_trend) }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #fff3e0;">👥</div>
          <div class="stat-value">{{ stats.active_users || 1 }}</div>
          <div class="stat-label">活跃用户</div>
          <div class="stat-trend positive">本周活跃</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 使用趋势图表 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="16">
        <el-card class="page-card">
          <div class="card-header">
            <h3>使用趋势</h3>
            <el-radio-group v-model="trendPeriod" size="small" @change="loadTrendData">
              <el-radio-button label="week">最近7天</el-radio-button>
              <el-radio-button label="month">最近30天</el-radio-button>
              <el-radio-button label="year">最近一年</el-radio-button>
            </el-radio-group>
          </div>
          <div class="trend-chart">
            <div v-for="(item, index) in trendData" :key="index" class="trend-item">
              <div class="trend-date">{{ item.date }}</div>
              <div class="trend-bars">
                <div class="trend-bar-group">
                  <div class="trend-bar upload" :style="{ height: item.uploadHeight }">
                    <span class="trend-value">{{ item.uploads }}</span>
                  </div>
                  <div class="trend-bar-label">上传</div>
                </div>
                <div class="trend-bar-group">
                  <div class="trend-bar conversion" :style="{ height: item.conversionHeight }">
                    <span class="trend-value">{{ item.conversions }}</span>
                  </div>
                  <div class="trend-bar-label">转换</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="page-card">
          <div class="card-header">
            <h3>操作分布</h3>
          </div>
          <div class="operation-stats">
            <div v-for="op in operationStats" :key="op.name" class="operation-item">
              <div class="operation-info">
                <span class="operation-icon">{{ op.icon }}</span>
                <span class="operation-name">{{ op.name }}</span>
              </div>
              <div class="operation-count">{{ op.count }}</div>
              <el-progress 
                :percentage="op.percentage" 
                :stroke-width="8"
                :show-text="false"
                :color="op.color"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 热门材料和格式 -->
    <el-row :gutter="16" class="section-row">
      <el-col :span="12">
        <el-card class="page-card">
          <div class="card-header">
            <h3>热门材料 TOP 10</h3>
          </div>
          <el-table :data="topMaterials" stripe max-height="400">
            <el-table-column type="index" label="排名" width="70" />
            <el-table-column prop="name" label="材料名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="viewCount" label="查看次数" width="100" align="center">
              <template #default="scope">
                <el-tag type="primary">{{ scope.row.viewCount }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="exportCount" label="导出次数" width="100" align="center">
              <template #default="scope">
                <el-tag type="success">{{ scope.row.exportCount }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="page-card">
          <div class="card-header">
            <h3>导出格式统计</h3>
          </div>
          <div class="format-stats">
            <div v-for="format in formatStats" :key="format.name" class="format-item">
              <div class="format-header">
                <span class="format-icon">{{ format.icon }}</span>
                <span class="format-name">{{ format.name }}</span>
                <span class="format-count">{{ format.count }}</span>
              </div>
              <el-progress 
                :percentage="format.percentage" 
                :stroke-width="16"
                :color="format.color"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统活动日志 -->
    <el-card class="page-card section-row">
      <div class="card-header">
        <h3>最近活动</h3>
        <el-button size="small" @click="loadActivityLog">刷新</el-button>
      </div>
      <el-timeline>
        <el-timeline-item
          v-for="activity in activityLog"
          :key="activity.id"
          :timestamp="activity.time"
          :type="activity.type"
          placement="top"
        >
          <div class="activity-content">
            <span class="activity-icon">{{ activity.icon }}</span>
            <span class="activity-text">{{ activity.text }}</span>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getStatistics } from '../api/material'

const stats = ref({
  total_materials: 0,
  total_uploads: 0,
  total_conversions: 0,
  active_users: 1,
  material_trend: 5,
  upload_trend: 8,
  conversion_trend: 3
})
const trendPeriod = ref('week')
const trendData = ref([])
const operationStats = ref([])
const topMaterials = ref([])
const formatStats = ref([])
const activityLog = ref([])

function getTrendClass(trend) {
  if (trend > 0) return 'positive'
  if (trend < 0) return 'negative'
  return 'neutral'
}

function getTrendText(trend) {
  if (trend > 0) return `↑ ${trend}%`
  if (trend < 0) return `↓ ${Math.abs(trend)}%`
  return '→ 0%'
}

function loadTrendData() {
  // 模拟趋势数据
  const days = trendPeriod.value === 'week' ? 7 : trendPeriod.value === 'month' ? 30 : 12
  const data = []
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const uploads = Math.floor(Math.random() * 20) + 5
    const conversions = Math.floor(Math.random() * 15) + 3
    
    data.push({
      date: trendPeriod.value === 'year' 
        ? `${date.getMonth() + 1}月` 
        : `${date.getMonth() + 1}/${date.getDate()}`,
      uploads,
      conversions,
      uploadHeight: `${(uploads / 25) * 100}%`,
      conversionHeight: `${(conversions / 20) * 100}%`
    })
  }
  
  trendData.value = data
}

function loadOperationStats() {
  const totalOps = stats.value.total_uploads + stats.value.total_conversions + 50
  
  operationStats.value = [
    {
      name: '文件上传',
      icon: '📤',
      count: stats.value.total_uploads || 45,
      percentage: Math.round(((stats.value.total_uploads || 45) / totalOps) * 100),
      color: '#409eff'
    },
    {
      name: '格式转换',
      icon: '🔄',
      count: stats.value.total_conversions || 38,
      percentage: Math.round(((stats.value.total_conversions || 38) / totalOps) * 100),
      color: '#67c23a'
    },
    {
      name: '数据验证',
      icon: '✅',
      count: 32,
      percentage: Math.round((32 / totalOps) * 100),
      color: '#e6a23c'
    },
    {
      name: '材料查看',
      icon: '👁️',
      count: 28,
      percentage: Math.round((28 / totalOps) * 100),
      color: '#f56c6c'
    }
  ]
}

function loadTopMaterials() {
  // 模拟热门材料数据
  topMaterials.value = [
    { name: 'AL6061 铝合金', viewCount: 45, exportCount: 23 },
    { name: 'AISI-1015 钢材', viewCount: 38, exportCount: 19 },
    { name: 'INCONEL-625 高温合金', viewCount: 32, exportCount: 15 },
    { name: 'A-286 不锈钢', viewCount: 28, exportCount: 14 },
    { name: 'CuZn37 黄铜', viewCount: 25, exportCount: 12 },
    { name: 'TI-TYPE-1 钛合金', viewCount: 22, exportCount: 11 },
    { name: 'C10100 纯铜', viewCount: 18, exportCount: 9 },
    { name: 'DIN-AlMgMn 铝镁锰合金', viewCount: 15, exportCount: 8 },
    { name: 'INCOLOY-901 镍基合金', viewCount: 12, exportCount: 6 },
    { name: 'U700 高温合金', viewCount: 10, exportCount: 5 }
  ]
}

function loadFormatStats() {
  const total = 100
  formatStats.value = [
    {
      name: 'Excel 模板',
      icon: '📊',
      count: 35,
      percentage: 35,
      color: '#67c23a'
    },
    {
      name: 'JSON 格式',
      icon: '📄',
      count: 28,
      percentage: 28,
      color: '#409eff'
    },
    {
      name: 'Abaqus INP',
      icon: '🔧',
      count: 22,
      percentage: 22,
      color: '#e6a23c'
    },
    {
      name: 'CSV 格式',
      icon: '📋',
      count: 10,
      percentage: 10,
      color: '#909399'
    },
    {
      name: 'TXT 格式',
      icon: '📝',
      count: 5,
      percentage: 5,
      color: '#c0c4cc'
    }
  ]
}

function loadActivityLog() {
  // 模拟活动日志
  const now = new Date()
  activityLog.value = [
    {
      id: 1,
      time: formatTime(new Date(now - 5 * 60000)),
      type: 'primary',
      icon: '📤',
      text: '上传了材料文件 AL6061_Machining_s000008.KEY'
    },
    {
      id: 2,
      time: formatTime(new Date(now - 15 * 60000)),
      type: 'success',
      icon: '🔄',
      text: '将材料 AISI-1015 转换为 Excel 格式'
    },
    {
      id: 3,
      time: formatTime(new Date(now - 30 * 60000)),
      type: 'warning',
      icon: '✅',
      text: '验证了材料 INCONEL-625 的数据完整性'
    },
    {
      id: 4,
      time: formatTime(new Date(now - 45 * 60000)),
      type: 'info',
      icon: '👁️',
      text: '查看了材料 A-286 的详细信息'
    },
    {
      id: 5,
      time: formatTime(new Date(now - 60 * 60000)),
      type: 'primary',
      icon: '📤',
      text: '批量上传了 3 个材料文件'
    },
    {
      id: 6,
      time: formatTime(new Date(now - 90 * 60000)),
      type: 'success',
      icon: '🔄',
      text: '批量转换了 5 个材料为 JSON 格式'
    },
    {
      id: 7,
      time: formatTime(new Date(now - 120 * 60000)),
      type: 'info',
      icon: '⭐',
      text: '收藏了材料 CuZn37 黄铜'
    },
    {
      id: 8,
      time: formatTime(new Date(now - 150 * 60000)),
      type: 'warning',
      icon: '🏷️',
      text: '为材料添加了标签：高温、锻造'
    }
  ]
}

function formatTime(time) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadStats() {
  try {
    const { data } = await getStatistics()
    stats.value = {
      total_materials: data.total_materials || 0,
      total_uploads: data.total_materials || 0,
      total_conversions: Math.floor((data.total_materials || 0) * 0.8),
      active_users: 1,
      material_trend: 5,
      upload_trend: 8,
      conversion_trend: 3
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(async () => {
  await loadStats()
  loadTrendData()
  loadOperationStats()
  loadTopMaterials()
  loadFormatStats()
  loadActivityLog()
})
</script>

<style scoped>
.statistics-page { display: grid; gap: 16px; }
.subtitle { margin: -8px 0 0; color: #64748b; }
.section-row { margin-top: 16px; }
.stat-card { text-align: center; border-radius: 14px; position: relative; }
.stat-icon { width: 60px; height: 60px; margin: 0 auto 12px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.stat-value { font-size: 32px; font-weight: 800; color: #0f172a; margin-bottom: 8px; }
.stat-label { color: #64748b; font-size: 14px; margin-bottom: 4px; }
.stat-trend { font-size: 12px; font-weight: 600; }
.stat-trend.positive { color: #67c23a; }
.stat-trend.negative { color: #f56c6c; }
.stat-trend.neutral { color: #909399; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.card-header h3 { margin: 0; font-size: 18px; font-weight: 600; }
.trend-chart { display: flex; gap: 8px; padding: 20px 0; overflow-x: auto; }
.trend-item { flex: 1; min-width: 60px; display: flex; flex-direction: column; align-items: center; }
.trend-date { font-size: 12px; color: #64748b; margin-bottom: 8px; }
.trend-bars { display: flex; gap: 4px; height: 150px; align-items: flex-end; }
.trend-bar-group { display: flex; flex-direction: column; align-items: center; }
.trend-bar { width: 24px; background: linear-gradient(180deg, #409eff, #66b1ff); border-radius: 4px 4px 0 0; position: relative; min-height: 20px; display: flex; align-items: flex-start; justify-content: center; transition: all 0.3s; }
.trend-bar.upload { background: linear-gradient(180deg, #409eff, #66b1ff); }
.trend-bar.conversion { background: linear-gradient(180deg, #67c23a, #85ce61); }
.trend-bar:hover { opacity: 0.8; }
.trend-value { font-size: 10px; color: white; font-weight: 600; padding: 2px; }
.trend-bar-label { font-size: 10px; color: #909399; margin-top: 4px; }
.operation-stats { display: grid; gap: 16px; }
.operation-item { display: grid; gap: 8px; }
.operation-info { display: flex; align-items: center; gap: 8px; }
.operation-icon { font-size: 20px; }
.operation-name { font-weight: 500; color: #475569; flex: 1; }
.operation-count { font-size: 24px; font-weight: 700; color: #0f172a; }
.format-stats { display: grid; gap: 16px; }
.format-item { display: grid; gap: 8px; }
.format-header { display: flex; align-items: center; gap: 8px; }
.format-icon { font-size: 20px; }
.format-name { font-weight: 500; color: #475569; flex: 1; }
.format-count { font-size: 18px; font-weight: 700; color: #0f172a; }
.activity-content { display: flex; align-items: center; gap: 8px; }
.activity-icon { font-size: 18px; }
.activity-text { color: #475569; }
</style>
