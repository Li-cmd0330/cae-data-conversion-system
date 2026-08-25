# GitHub 上传指南

## 推荐仓库信息

Repository name:

```text
cae-data-conversion-system
```

Description:

```text
A Django + Vue based data conversion system for CAE simulation pre-processing.
```

Topics:

```text
cae, simulation, data-conversion, django, vue, vite, materials, lsdyna
```

## 首次上传步骤

在项目根目录执行：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/cae-data-conversion-system.git
git push -u origin main
```

将 `<your-username>` 替换为你的 GitHub 用户名。

## 上传前检查

建议确认这些文件不会被上传：

```text
backend/venv/
backend/db.sqlite3
backend/media/
frontend/node_modules/
frontend/dist/
```

这些目录和文件已经写入 `.gitignore`，正常情况下 Git 不会跟踪它们。

## 建议提交内容

适合上传：

- 前后端源码
- `requirements.txt`
- `package.json` 和 `package-lock.json`
- 启动脚本
- README、许可证、环境变量示例
- 脱敏后的示例材料文件

不建议上传：

- 虚拟环境
- 依赖缓存
- 构建产物
- 本地数据库
- 用户上传文件
- 包含隐私或未公开实验数据的材料文件
