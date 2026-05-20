import re
with open(r'D:\Desktop\ysunet\src\ysu_net_login\gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'def _change_theme' in line or 'def _apply_mica' in line or 'def _save_wifi_setting' in line:
        print(f'{i}: {line.rstrip()}')
        for j in range(i, min(i+20, len(lines)+1)):
            print(f'  {j}: {lines[j-1].rstrip()}')
        print('---')
