# CAE Simulation Pre-processing Data Conversion System

面向仿真 CAE 前处理的数据转换系统。项目以材料参数文件解析、数据校验、材料管理和格式导出为核心，帮助将工程仿真中常见的材料数据整理为更规范、可复用、可视化的数据资产。

## 项目简介

本项目是一个前后端分离的 Web 系统：

- 后端基于 Django 与 Django REST framework，负责文件解析、材料数据管理、校验、导出和统计接口。
- 前端基于 Vue 3、Vite、Element Plus 与 ECharts，提供文件上传、材料管理、数据可视化、转换导出和统计分析页面。
- 支持 LS-DYNA KEY 等材料文件的解析，并围绕材料参数、流动应力数据和完整性校验提供辅助功能。

## 主要功能

- 材料文件上传与批量上传
- 材料基础参数解析、归一化与持久化
- 材料数据完整性校验
- 材料数据管理、搜索、收藏、标签维护
- 相似材料推荐与智能搜索
- 材料参数对比与统计分析
- 流动应力曲线、完整性雷达图等可视化展示
- JSON 等目标格式导出

## 技术栈

后端：

- Python 3.10+
- Django 5
- Django REST framework
- pandas / NumPy / SciPy / openpyxl
- SQLite

前端：

- Vue 3
- Vite
- Vue Router
- Pinia
- Element Plus
- Axios
- ECharts

## 项目结构

```text
.
├── backend/                 # Django 后端服务
│   ├── apps/                # 业务应用：材料、转换、校验、算法
│   ├── core/                # 解析、导出、校验、可视化和智能检索核心模块
│   ├── cae_converter/       # Django 项目配置
│   ├── manage.py
│   └── requirements.txt
├── frontend/                # Vue 前端应用
│   ├── src/
│   │   ├── api/             # 接口请求封装
│   │   ├── components/      # 通用组件
│   │   ├── router/          # 路由配置
│   │   ├── store/           # 状态管理
│   │   └── views/           # 页面视图
│   ├── package.json
│   └── vite.config.js
├── START_HERE.bat           # Windows 一键启动脚本
├── backend_start.bat        # 后端启动脚本
├── frontend_start.bat       # 前端启动脚本
└── .env.example             # 环境变量示例
```

## 快速开始

### 方式一：Windows 一键启动

双击项目根目录下的 `START_HERE.bat`，脚本会分别启动后端和前端服务。

启动后访问：

```text
http://127.0.0.1:5173/
```

### 方式二：手动启动

启动后端：

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

启动前端：

```bash
cd frontend
npm install
npm run dev
```

前端开发服务默认运行在：

```text
http://127.0.0.1:5173/
```

后端接口默认运行在：

```text
http://127.0.0.1:8000/
```

## 环境变量

可以复制 `.env.example` 中的配置，并按部署环境设置：

```text
DJANGO_SECRET_KEY=change-me-before-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOW_ALL_ORIGINS=True
```

说明：

- 本地开发可以保留 `DJANGO_DEBUG=True`。
- 部署到服务器时应设置强随机 `DJANGO_SECRET_KEY`，并将 `DJANGO_DEBUG` 改为 `False`。
- `DJANGO_ALLOWED_HOSTS` 应填写实际访问域名或服务器 IP。

## API 模块

系统后端主要接口按功能拆分：

- `/api/materials/`：材料上传、管理、搜索、统计、图表数据
- `/api/conversion/`：材料数据格式转换
- `/api/validation/`：数据校验
- `/api/algorithms/`：算法相关接口

## 上传到 GitHub 前建议

本仓库已经配置 `.gitignore`，默认不会上传以下本地生成内容：

- `frontend/node_modules/`
- `frontend/dist/`
- `backend/venv/`
- `backend/db.sqlite3`
- `backend/media/`
- Python 缓存文件与系统临时文件

如果示例 Excel 或 KEY 文件用于演示，可以保留在仓库中；如果包含未公开实验数据，建议删除或替换为脱敏示例。

## 适用场景

- CAE 仿真前处理材料数据整理
- 材料模型参数转换与校验
- 毕业设计、课程设计或工程软件原型展示
- LS-DYNA 等仿真输入文件的数据分析辅助

## License

This project is licensed under the MIT License.
