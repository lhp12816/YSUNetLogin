# YSUNetLogin

燕山大学校园网登录图形界面工具

## 功能特性

- **一键登录**：支持校园网、中国联通、中国电信、中国移动
- **验证码支持**：自动检测并弹窗输入验证码
- **状态监控**：实时查看网络连接状态（IP、接入位置、认证时间等）
- **设备详情**：查看当前在线设备的完整信息（MAC、VLAN、登录方式等）
- **账户信息**：查看已用流量、在线时长、余额等
- **自动重连**：掉线后自动重新登录（可选）
- **密码管理**：安全保存密码，支持查看/清除
- **WiFi 连接**：手动切换至校园网 WiFi（iYanDa）
- **深色主题**：现代 Material Design 风格界面

## 下载使用

### 直接运行（推荐）

下载 `YSUNetLogin.exe`，双击运行即可，无需安装任何依赖。

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/YSUNetLogin.git
cd YSUNetLogin

# 创建虚拟环境并安装依赖
uv sync

# 运行 GUI
uv run python -m ysu_net_login.gui
```

## 打包为 EXE

```bash
uv run python build_exe.py
```

输出文件：`dist/YSUNetLogin.exe`

## 配置文件

配置文件位置：`%USERPROFILE%\.ysunetlogin\gui_config.json`

包含：用户名、密码（加密存储）、服务选择、自动登录、代理设置等。

## 技术栈

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代 tkinter 主题
- [requests](https://requests.readthedocs.io/) - HTTP 请求
- [PyInstaller](https://pyinstaller.org/) - EXE 打包
- [pycryptodome](https://www.pycryptodome.org/) - AES 加密

## 免责声明

本项目仅供学习和个人使用，不保证网络认证的稳定性。请遵守燕山大学网络使用相关规定。

## 许可

MIT License
