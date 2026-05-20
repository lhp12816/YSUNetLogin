"""WiFi 管理器 - 自动连接校园网"""
import subprocess
import re
import sys
from typing import Optional, List, Tuple

WIFI_SSID = "iYanDa"

_SUBPROC_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

def _get_startupinfo():
    if sys.platform != "win32":
        return None
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    return si


class WiFiManager:
    """通过 netsh 管理 Windows WiFi 连接"""

    @staticmethod
    def get_current_ssid() -> Optional[str]:
        """获取当前连接的 WiFi SSID"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=5,
                creationflags=_SUBPROC_FLAGS, startupinfo=_get_startupinfo()
            )
            output = result.stdout
            match = re.search(r"SSID\s*:\s*(.+)", output)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return None

    @staticmethod
    def get_profiles() -> List[str]:
        """获取已保存的 WiFi 配置文件列表"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=5,
                creationflags=_SUBPROC_FLAGS, startupinfo=_get_startupinfo()
            )
            output = result.stdout
            profiles = re.findall(r"所有用户配置文件\s*:\s*(.+)", output)
            if not profiles:
                profiles = re.findall(r"User profiles\s*.*\r?\n?.*:\s*(.+)", output)
            if not profiles:
                profiles = re.findall(r":\s*(.+)", output)
            return [p.strip() for p in profiles if p.strip()]
        except Exception:
            return []

    @staticmethod
    def connect(ssid: str = WIFI_SSID) -> Tuple[bool, str]:
        """连接到指定 WiFi（若已连接则跳过）"""
        current = WiFiManager.get_current_ssid()
        if current and ssid.lower() in current.lower():
            return True, f"当前已连接到 {current}"
        try:
            result = subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=15,
                creationflags=_SUBPROC_FLAGS, startupinfo=_get_startupinfo()
            )
            if "已成功完成" in result.stdout or "successfully" in result.stdout.lower():
                return True, f"已连接到 {ssid}"
            if result.returncode == 0:
                return True, f"已尝试连接 {ssid}"
            return False, f"连接失败: {result.stdout or result.stderr}"
        except Exception as e:
            return False, f"连接异常: {e}"

    @staticmethod
    def is_wifi_enabled() -> bool:
        """检查 WiFi 是否开启"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=5,
                creationflags=_SUBPROC_FLAGS, startupinfo=_get_startupinfo()
            )
            return "状态" in result.stdout or "State" in result.stdout or "SSID" in result.stdout
        except Exception:
            return False

    @staticmethod
    def is_connected_to_campus() -> bool:
        """检查是否已连接到校园网 WiFi"""
        ssid = WiFiManager.get_current_ssid()
        if not ssid:
            return False
        campus_names = [WIFI_SSID, "iYanDa", "YSU", "YanShan", "燕山大学", "校园网"]
        return any(name.lower() in ssid.lower() for name in campus_names)
