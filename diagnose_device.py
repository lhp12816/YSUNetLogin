import sys
sys.path.insert(0, r'D:\Desktop\ysunet\src')
from ysu_net_login.ruijie_client import RuijieClient
import json

try:
    client = RuijieClient()
    data = client.get_online_user_info()
    print("=== getOnlineUserInfo 原始返回 ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"错误: {e}")

input("\n按 Enter 退出...")
