"""
打包脚本 - 使用 PyInstaller 将 YSUNetLogin GUI 打包为独立可执行文件

使用方法:
    1. 确保已安装 Python 3.8+
    2. 运行: uv run build_exe.py
    3. 或: python build_exe.py

输出:
    dist/YSUNetLogin.exe - 单文件可执行程序
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"
GUI_ENTRY = SRC_DIR / "ysu_net_login" / "gui.py"
LAUNCHER = PROJECT_ROOT / "gui_launcher.py"

def run(cmd, **kwargs):
    """运行命令并打印输出"""
    print(f">>> {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    return result

def ensure_pyinstaller():
    """确保 PyInstaller 已安装"""
    try:
        import PyInstaller
        print("PyInstaller 已安装")
        return
    except ImportError:
        print("正在安装 PyInstaller...")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"], cwd=PROJECT_ROOT, check=True)

def build():
    """打包主程序"""
    print("\n=== 开始打包 YSUNetLogin GUI ===\n")
    
    # 使用 launcher 作为入口，因为它有正确的 sys.path 处理
    entry_point = str(LAUNCHER)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "YSUNetLogin",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--add-data", f"{SRC_DIR}{os.pathsep}src",
        # 核心模块
        "--hidden-import", "ysu_net_login.ruijie_client",
        "--hidden-import", "ysu_net_login.config",
        "--hidden-import", "ysu_net_login.ysu_login",
        # 网络请求
        "--hidden-import", "requests",
        "--hidden-import", "urllib3",
        "--hidden-import", "urllib3.util",
        "--hidden-import", "urllib3.connection",
        "--hidden-import", "urllib3.response",
        "--hidden-import", "urllib3.contrib",
        "--hidden-import", "urllib3.contrib.pyopenssl",
        "--hidden-import", "urllib3.packages",
        "--hidden-import", "urllib3.packages.ssl_match_hostname",
        "--hidden-import", "urllib3._collections",
        "--hidden-import", "urllib3.fields",
        "--hidden-import", "urllib3.filepost",
        "--hidden-import", "urllib3.request",
        "--hidden-import", "urllib3.poolmanager",
        "--hidden-import", "urllib3.connectionpool",
        "--hidden-import", "urllib3.exceptions",
        "--hidden-import", "urllib3.util.connection",
        "--hidden-import", "urllib3.util.request",
        "--hidden-import", "urllib3.util.response",
        "--hidden-import", "urllib3.util.retry",
        "--hidden-import", "urllib3.util.ssl_",
        "--hidden-import", "urllib3.util.timeout",
        "--hidden-import", "urllib3.util.url",
        # SSL/证书
        "--hidden-import", "certifi",
        "--hidden-import", "charset_normalizer",
        "--hidden-import", "idna",
        "--hidden-import", "idna.idnadata",
        "--hidden-import", "idna.package_data",
        # 加密
        "--hidden-import", "Crypto",
        "--hidden-import", "Crypto.Cipher",
        "--hidden-import", "Crypto.Cipher.AES",
        "--hidden-import", "Crypto.Util.Padding",
        "--hidden-import", "Crypto.Util",
        "--hidden-import", "Crypto.Random",
        "--hidden-import", "Crypto.Protocol",
        # HTML解析
        "--hidden-import", "bs4",
        "--hidden-import", "beautifulsoup4",
        "--hidden-import", "soupsieve",
        # 图像处理
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        # 收集完整包
        "--collect-all", "customtkinter",
        "--collect-all", "darkdetect",
        "--collect-all", "requests",
        "--collect-all", "urllib3",
        "--collect-all", "certifi",
        "--collect-all", "charset_normalizer",
        "--collect-all", "idna",
        "--collect-all", "bs4",
        "--collect-all", "Pillow",
        entry_point
    ]
    
    result = run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print(f"\n✅ 打包成功！")
        print(f"📦 输出文件: {PROJECT_ROOT / 'dist' / 'YSUNetLogin.exe'}")
        print(f"📁 输出目录: {PROJECT_ROOT / 'dist'}")
        print(f"\n💡 提示: 可以将 exe 文件复制到桌面或任意位置使用")
    else:
        print(f"\n❌ 打包失败，请检查上面的错误信息")
        sys.exit(1)

if __name__ == "__main__":
    ensure_pyinstaller()
    build()
