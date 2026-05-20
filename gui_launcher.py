"""
YSUNetLogin GUI 启动器
直接双击运行此文件即可启动图形界面
"""

import sys
from pathlib import Path

# 确保 src 目录在路径中
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ysu_net_login.gui import main

if __name__ == "__main__":
    main()
