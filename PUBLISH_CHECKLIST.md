## 发布前最终检查清单

### 代码质量
- [ ] `gui.py` 语法正确，无运行时错误
- [ ] `ruijie_client.py` 字段名与 API 实际返回匹配
- [ ] `wifi_manager.py` 所有 subprocess 调用已隐藏 CMD 窗口
- [ ] 启动时不执行任何自动 WiFi 操作
- [ ] 深色主题固定，无浅色模式切换

### 文件完整性
- [ ] 核心认证文件来自原项目（已标注）
- [ ] 新增文件已正确归属
- [ ] 临时测试脚本已删除
- [ ] `.gitignore` 已排除 `.venv/`、`dist/`、`gui_config.json`

### 文档完整性
- [ ] README 包含项目来源与归属声明
- [ ] README 包含 AI 参与开发说明
- [ ] LICENSE 为 MIT
- [ ] RELEASE_NOTES.md 已编写

### 构建产物
- [ ] `dist/YSUNetLogin.exe` 已生成（约 24MB）
- [ ] EXE 可独立运行，无额外依赖

### Git 仓库
- [ ] 远程仓库已配置为 `https://github.com/Halck/YSUNetLogin.git`
- [ ] 分支为 `main`
- [ ] 所有更改已提交

---

## 发布方式（因网络问题无法自动推送）

### 方式一：手动推送（推荐）
在 PowerShell 执行：
```powershell
cd D:\Desktop\ysunet
git push -u origin main
```
若失败，尝试设置代理后重试。

### 方式二：GitHub 网页上传
1. 访问 https://github.com/Halck/YSUNetLogin
2. 点击 "Add file" → "Upload files"
3. 拖拽 `D:\Desktop\ysunet` 下所有文件（除 `.venv/`、`dist/`、`.git/`）
4. 提交更改
5. 在 Releases 中上传 `dist/YSUNetLogin.exe`

### 方式三：使用 Gitee 镜像
若 GitHub 持续无法访问，可考虑同步发布到 Gitee：
```powershell
cd D:\Desktop\ysunet
git remote add gitee https://gitee.com/Halck/YSUNetLogin.git
git push -u gitee main
```
