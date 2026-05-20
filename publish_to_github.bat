@echo off
chcp 65001 >nul
echo === YSUNetLogin GitHub 发布脚本 ===
echo.

:: 检查是否已登录 GitHub（浏览器）
echo [1/4] 检查网络连接...
ping github.com -n 1 -w 3000 >nul
if %errorlevel% neq 0 (
    echo ❌ 无法连接到 GitHub，请开启代理/VPN后重试
    pause
    exit /b 1
)

echo [2/4] 设置 Git 远程仓库...
cd /d D:\Desktop\ysunet
git remote remove origin 2>nul
git remote add origin https://github.com/Halck/YSUNetLogin.git
git branch -M main

echo [3/4] 推送代码到 GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 推送失败，请检查 GitHub 仓库是否已创建，或尝试设置代理
    echo 设置代理命令：git config --global http.proxy http://127.0.0.1:7890
    pause
    exit /b 1
)

echo [4/4] 推送成功！
echo.
echo 请访问 https://github.com/Halck/YSUNetLogin/releases 创建 Release
echo 上传文件：D:\Desktop\ysunet\dist\YSUNetLogin.exe
echo.
pause
