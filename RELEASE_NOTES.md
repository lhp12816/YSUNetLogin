# YSUNetLogin v1.0.0

## 新增功能

- **图形界面**：基于 customtkinter 的现代深色主题 GUI，替代命令行操作
- **验证码弹窗**：自动检测验证码，弹出输入对话框
- **状态监控**：实时显示 IP、接入位置、认证时间、在线状态
- **在线设备详情**：查看当前设备的完整网络参数（MAC、VLAN、登录方式、SSID 等）
- **账户信息**：显示已用流量、在线时长、余额等（字段名跟随服务器返回）
- **WiFi 管理**：一键连接校园网 WiFi（iYanDa），手动触发
- **自动重连**：掉线后自动重新登录（可选）
- **密码管理**：加密保存密码，支持查看/清除
- **独立 EXE**：PyInstaller 打包，零依赖，双击运行

## 技术改进

- 所有网络操作改为后台线程，UI 不卡顿
- 修复原项目字段名与 API 实际返回不匹配的问题
- 移除启动时的 WiFi 自动切换，避免干扰现有连接
- 隐藏所有 subprocess CMD 窗口

## 文件归属

- 核心认证逻辑来自 [KamijoToma/YSUNetLoginv2](https://github.com/KamijoToma/YSUNetLoginv2)
- 图形界面、WiFi 管理、打包脚本为本项目新增

## 下载

- `YSUNetLogin.exe`（Windows 10/11，无需安装）
