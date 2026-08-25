<template>
  <el-container class="layout">
    <el-aside width="260px" class="sidebar">
      <div class="brand">
        <span class="brand-icon">🎯</span>
        <span class="brand-text">锻造仿真CAE前处理数据转换系统</span>
      </div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item index="/">
          <span class="menu-icon">📊</span>
          <span>系统概览</span>
        </el-menu-item>
        <el-menu-item index="/upload">
          <span class="menu-icon">📤</span>
          <span>文件上传</span>
        </el-menu-item>
        <el-menu-item index="/manage">
          <span class="menu-icon">📋</span>
          <span>材料管理</span>
        </el-menu-item>
        <el-menu-item index="/materials">
          <span class="menu-icon">🔍</span>
          <span>材料详情</span>
        </el-menu-item>
        <el-menu-item index="/validation">
          <span class="menu-icon">✅</span>
          <span>数据验证</span>
        </el-menu-item>
        <el-menu-item index="/conversion">
          <span class="menu-icon">🔄</span>
          <span>格式转换</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <span class="menu-icon">📈</span>
          <span>使用统计</span>
        </el-menu-item>
        <el-menu-item index="/algorithms">
          <span class="menu-icon">🧮</span>
          <span>材料算法分析</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="footer-info">
          <span class="footer-label">系统版本</span>
          <span class="footer-value">v2.1.0</span>
        </div>
        <div class="footer-info">
          <span class="footer-label">在线状态</span>
          <span class="footer-status">
            <span class="status-indicator"></span>
            正常运行
          </span>
        </div>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="header-title">锻造仿真CAE前处理数据转换系统</span>
        <div class="header-actions">
          <el-badge :value="3" class="header-badge">
            <el-button circle size="small">🔔</el-button>
          </el-badge>
          <el-button circle size="small">⚙️</el-button>
          <el-button circle size="small">👤</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }
.layout { height: 100vh; }
.sidebar { 
  background: linear-gradient(180deg, #1a1f3a 0%, #2d3561 50%, #1a1f3a 100%);
  color: white; 
  display: flex; 
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
  position: relative;
}
.sidebar::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}
.brand { 
  padding: 24px 20px; 
  font-size: 14px; 
  font-weight: 700;
  line-height: 1.5;
  color: white; 
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 1;
}
.brand-icon {
  font-size: 24px;
  animation: rotate 20s linear infinite;
}
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.brand-text { flex: 1; }
.menu { 
  flex: 1;
  border: none; 
  background: transparent;
  padding: 12px 0;
  position: relative;
  z-index: 1;
}
.menu .el-menu-item { 
  color: rgba(255,255,255,0.85);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin: 4px 12px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  height: 48px;
}
.menu-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}
.menu .el-menu-item:hover { 
  background: rgba(255,255,255,0.12); 
  color: white;
  transform: translateX(6px);
}
.menu .el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.2) 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  color: white;
  font-weight: 600;
  border-left: 4px solid #667eea;
}
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
}
.footer-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
.footer-label { color: rgba(255,255,255,0.6); }
.footer-value { color: rgba(255,255,255,0.9); font-weight: 600; }
.footer-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,0.9);
  font-weight: 600;
}
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67c23a;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.95); }
}
.header { 
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  padding: 0 32px;
  position: relative;
  overflow: hidden;
}
.header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.header-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.header-badge { cursor: pointer; }
.el-main { 
  background: linear-gradient(135deg, #f8fafc 0%, #e9ecef 100%);
  padding: 24px; 
  overflow-y: auto;
}
.page-card { 
  border-radius: 16px; 
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-card:hover {
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.18);
  transform: translateY(-2px);
}
.page-title { 
  font-size: 28px; 
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}
.toolbar { 
  display: flex; 
  gap: 12px; 
  align-items: center; 
  flex-wrap: wrap;
}
</style>
