# YSUNetLogin GUI 使用指南

## 快速开始

### 方法一：直接运行（推荐）
```bash
# 使用 uv（推荐）
uv run gui_launcher.py

# 或使用 Python
python gui_launcher.py
```

### 方法二：安装为命令
```bash
# 安装项目
uv pip install -e .

# 启动 GUI
ysunetlogin-gui
```

### 方法三：打包为可执行文件
```bash
# 安装依赖并打包
uv run build_exe.py

# 打包完成后，双击 dist/YSUNetLogin.exe 即可运行
```

## 功能说明

### 登录页
- **用户名/密码**: 输入校园网账号信息
- **网络运营商**: 选择校园网/联通/电信/移动
- **记住密码**: 保存凭据到本地（加密存储在用户目录）
- **自动登录**: 启动时自动尝试登录（需先保存密码）
- **登录/登出**: 一键连接或断开校园网

### 状态页
- 实时显示网络连接状态（已连接/未连接）
- 显示用户名、运营商、IP地址、登录时间、接入位置
- 支持手动刷新状态

### 账户页
- 显示账户详细信息
- 包括网络使用详情和余额信息（如有）
- 支持滚动浏览大量信息

### 设置页
- **主题切换**: 深色/浅色/跟随系统
- **代理设置**: 配置 HTTP 代理（网络异常时使用）
- **数据管理**: 清除保存的密码和配置

## 配置存储位置

配置和保存的密码存储在：
- Windows: `%USERPROFILE%\.ysunetlogin\gui_config.json`
- macOS/Linux: `~/.ysunetlogin/gui_config.json`

## 界面预览

现代化暗色主题界面，左侧导航栏，右侧内容区：
- 圆角卡片式设计
- 清晰的视觉层次
- 实时状态指示器
- 底部操作日志

## 常见问题

**Q: 启动后窗口空白或报错？**
A: 确保已安装所有依赖：`uv pip install -r requirements.txt`

**Q: 登录按钮一直显示"登录中"？**
A: 检查是否连接到校园网 WiFi，或者查看代理设置是否正确

**Q: 打包后的 exe 很大？**
A: PyInstaller 单文件模式会包含 Python 运行时，约 30-50MB 是正常范围

**Q: 如何创建桌面快捷方式？**
A: 右键 `dist/YSUNetLogin.exe` → 发送到 → 桌面快捷方式
