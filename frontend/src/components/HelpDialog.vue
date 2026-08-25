<template>
  <el-dialog v-model="visible" title="使用帮助" width="800px" :close-on-click-modal="false">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="快速入门" name="quickstart">
        <div class="help-content">
          <h3>🚀 快速开始</h3>
          <el-steps :active="0" direction="vertical">
            <el-step title="步骤 1：上传 KEY 文件" description="在"文件上传"页面选择并上传 DEFORM KEY 格式的材料文件" />
            <el-step title="步骤 2：查看材料详情" description="上传成功后，在"材料详情"页面查看解析后的材料属性和流动应力曲线" />
            <el-step title="步骤 3：验证数据" description="在"数据验证"页面对材料数据进行完整性和合理性检查" />
            <el-step title="步骤 4：格式转换" description="在"格式转换"页面选择目标格式（Excel/JSON/CSV/TXT/Abaqus INP）并导出" />
          </el-steps>
        </div>
      </el-tab-pane>

      <el-tab-pane label="功能说明" name="features">
        <div class="help-content">
          <h3>📋 功能模块</h3>
          <el-collapse>
            <el-collapse-item title="📤 文件上传" name="1">
              <p><strong>功能：</strong>上传 DEFORM KEY 格式的材料文件并自动解析</p>
              <p><strong>支持：</strong>单文件上传、批量上传</p>
              <p><strong>注意：</strong>原始 KEY 文件解析后会自动删除，仅保留结构化数据</p>
            </el-collapse-item>
            
            <el-collapse-item title="📊 材料管理" name="2">
              <p><strong>功能：</strong>管理所有已上传的材料数据</p>
              <p><strong>支持：</strong>搜索、筛选、标签管理、收藏、批量操作</p>
              <p><strong>提示：</strong>可以为材料添加标签和备注，方便分类管理</p>
            </el-collapse-item>
            
            <el-collapse-item title="🔍 材料详情" name="3">
              <p><strong>功能：</strong>查看材料的详细属性和流动应力可视化</p>
              <p><strong>显示：</strong>材料名称、单位系统、所有物理属性、流动应力曲线</p>
              <p><strong>操作：</strong>可以清空历史材料数据</p>
            </el-collapse-item>
            
            <el-collapse-item title="✅ 数据验证" name="4">
              <p><strong>功能：</strong>验证材料数据的完整性和合理性</p>
              <p><strong>检查：</strong>必需字段、推荐字段、数值范围、物理一致性</p>
              <p><strong>结果：</strong>显示错误、警告和提示信息</p>
            </el-collapse-item>
            
            <el-collapse-item title="🔄 格式转换" name="5">
              <p><strong>功能：</strong>将材料数据转换为不同格式</p>
              <p><strong>支持格式：</strong>Excel模板、JSON、CSV、TXT、Abaqus INP</p>
              <p><strong>特点：</strong>支持批量转换，文件名自动匹配源文件</p>
            </el-collapse-item>
            
            <el-collapse-item title="📈 使用统计" name="6">
              <p><strong>功能：</strong>查看系统使用情况和数据趋势</p>
              <p><strong>显示：</strong>核心指标、使用趋势、热门材料、格式统计</p>
              <p><strong>用途：</strong>了解系统使用情况，优化工作流程</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <el-tab-pane label="常见问题" name="faq">
        <div class="help-content">
          <h3>❓ 常见问题</h3>
          <el-collapse>
            <el-collapse-item title="Q: 支持哪些文件格式？" name="q1">
              <p><strong>A:</strong> 目前仅支持 DEFORM KEY 格式的材料文件（.KEY 扩展名）。</p>
            </el-collapse-item>
            
            <el-collapse-item title="Q: 上传的原始文件会保留吗？" name="q2">
              <p><strong>A:</strong> 不会。为了节省存储空间，原始 KEY 文件在解析完成后会自动删除，系统仅保留结构化的材料数据。</p>
            </el-collapse-item>
            
            <el-collapse-item title="Q: 如何批量转换多个材料？" name="q3">
              <p><strong>A:</strong> 在"格式转换"页面，勾选多个材料，选择目标格式，点击"批量生成结果文件"即可。</p>
            </el-collapse-item>
            
            <el-collapse-item title="Q: 验证失败是什么原因？" name="q4">
              <p><strong>A:</strong> 验证失败通常是因为：</p>
              <ul>
                <li>缺少必需的材料属性字段</li>
                <li>数值超出合理范围</li>
                <li>流动应力数据不完整</li>
                <li>物理参数不一致</li>
              </ul>
              <p>请查看详细的验证报告了解具体问题。</p>
            </el-collapse-item>
            
            <el-collapse-item title="Q: 导出的文件在哪里？" name="q5">
              <p><strong>A:</strong> 导出后会显示下载链接，点击即可下载。文件保存在服务器的 media/exports 目录中。</p>
            </el-collapse-item>
            
            <el-collapse-item title="Q: 如何清空所有材料数据？" name="q6">
              <p><strong>A:</strong> 在"材料详情"页面，点击"清空历史材料"按钮，确认后即可删除所有材料数据。</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <el-tab-pane label="快捷键" name="shortcuts">
        <div class="help-content">
          <h3>⌨️ 快捷键</h3>
          <el-table :data="shortcuts" border>
            <el-table-column prop="key" label="快捷键" width="150" />
            <el-table-column prop="description" label="功能说明" />
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="关于" name="about">
        <div class="help-content">
          <h3>ℹ️ 关于系统</h3>
          <el-descriptions border :column="1">
            <el-descriptions-item label="系统名称">锻造仿真CAE前处理数据转换系统</el-descriptions-item>
            <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="开发框架">Vue 3 + Django + Element Plus</el-descriptions-item>
            <el-descriptions-item label="主要功能">材料数据解析、验证、转换、可视化</el-descriptions-item>
            <el-descriptions-item label="支持格式">DEFORM KEY → Excel/JSON/CSV/TXT/Abaqus INP</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button type="primary" @click="visible = false">我知道了</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const activeTab = ref('quickstart')

const shortcuts = [
  { key: 'Ctrl + H', description: '打开帮助文档' },
  { key: 'Ctrl + S', description: '保存当前编辑' },
  { key: 'Ctrl + F', description: '搜索材料' },
  { key: 'Esc', description: '关闭对话框' }
]

function show(tab = 'quickstart') {
  activeTab.value = tab
  visible.value = true
}

function hide() {
  visible.value = false
}

defineExpose({ show, hide })
</script>

<style scoped>
.help-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.help-content h3 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
}

.help-content p {
  margin: 8px 0;
  line-height: 1.6;
  color: #606266;
}

.help-content ul {
  margin: 8px 0;
  padding-left: 24px;
}

.help-content li {
  margin: 4px 0;
  color: #606266;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
}

:deep(.el-step__title) {
  font-size: 14px;
}
</style>
