"""
YSUNetLogin GUI - 燕山大学校园网登录图形界面
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import sys
import json
from pathlib import Path

_current_file = Path(__file__).resolve()
if _current_file.parent.name == "ysu_net_login":
    _project_root = _current_file.parent.parent.parent
else:
    _project_root = _current_file.parent
_src_path = str(_project_root / "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from ysu_net_login.ruijie_client import RuijieClient
from ysu_net_login.config import get_error_message
from ysu_net_login.wifi_manager import WiFiManager

ACCENT = {"primary": "#3B82F6", "primary_hover": "#2563EB",
          "success": "#10B981", "danger": "#EF4444", "warning": "#F59E0B"}
SERVICES = ["校园网", "中国联通", "中国电信", "中国移动"]
WIFI_SSID = "iYanDa"


class CaptchaDialog(ctk.CTkToplevel):
    def __init__(self, parent, captcha_path=None):
        super().__init__(parent)
        self.title("验证码")
        self.geometry("320x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.captcha_code = None
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="请输入验证码", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        if captcha_path and os.path.exists(captcha_path):
            try:
                from PIL import Image
                img = Image.open(captcha_path)
                img.thumbnail((200, 80))
                from customtkinter import CTkImage
                photo = CTkImage(img, size=img.size)
                ctk.CTkLabel(frame, image=photo, text="").pack(pady=5)
            except Exception:
                ctk.CTkLabel(frame, text="[验证码图片加载失败]", text_color=ACCENT["warning"]).pack(pady=5)
        else:
            ctk.CTkLabel(frame, text="请查看弹出的验证码图片", text_color=("gray40", "gray60")).pack(pady=5)
        self.entry = ctk.CTkEntry(frame, placeholder_text="输入验证码", height=35, font=ctk.CTkFont(size=14))
        self.entry.pack(fill="x", pady=10)
        self.entry.bind("<Return>", lambda e: self._submit())
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="取消", fg_color="transparent",
                      hover_color=("gray85", "gray40"), command=self._cancel).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="确认", fg_color=ACCENT["primary"],
                      hover_color=ACCENT["primary_hover"], command=self._submit).pack(side="right")
        self.entry.focus()
        self.wait_window(self)

    def _submit(self):
        self.captcha_code = self.entry.get().strip()
        self.destroy()

    def _cancel(self):
        self.captcha_code = None
        self.destroy()


class YSUNetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YSUNetLogin - 燕山大学校园网登录")
        self.geometry("900x650")
        self.minsize(800, 600)
        self.data_dir = Path.home() / ".ysunetlogin"
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "gui_config.json"
        self.app_config = self._load_config()
        ctk.set_appearance_mode("dark")
        self.client = None
        self.current_user = self.app_config.get("username", "")
        self.current_service = self.app_config.get("service", "校园网")
        self.is_logged_in = False
        self.pages = {}
        self.account_rows = []
        self.status_fields = {}
        self.nav_buttons = {}
        self._setup_layout()
        self._build_sidebar()
        self._build_pages_container()
        self._build_status_bar()
        self.show_page("login")
        self.after(600, self._startup_checks)

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"username": "", "password": "", "save_password": False,
                "service": "校园网", "auto_login": False, "auto_wifi": False,
                "proxy": "",
                "auto_reconnect_enabled": False, "auto_reconnect_interval": 5,
                "auto_reconnect_use_saved_account": True,
                "auto_reconnect_username": "", "auto_reconnect_password": "",
                "auto_reconnect_service": "校园网"}

    def _save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.app_config, f, ensure_ascii=False, indent=2)

    def _setup_layout(self):
        self.grid_columnconfigure(0, minsize=200, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("gray92", "gray14"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="YSUNetLogin", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=ACCENT["primary"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="燕山大学校园网", font=ctk.CTkFont(size=12),
                     text_color=("gray50", "gray60")).pack(anchor="w")
        nav_items = [("login", "  登录"), ("status", "  状态"), ("device", "  设备"), ("account", "  账户"), ("settings", "  设置")]
        for key, icon_text in nav_items:
            btn = ctk.CTkButton(self.sidebar, text=icon_text, anchor="w", font=ctk.CTkFont(size=14),
                                fg_color="transparent", height=45, corner_radius=10,
                                command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[key] = btn
        sidebar_status = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=40)
        sidebar_status.pack(side="bottom", fill="x", padx=15, pady=15)
        self.status_dot = ctk.CTkLabel(sidebar_status, text="●", font=ctk.CTkFont(size=16),
                                       text_color=ACCENT["danger"])
        self.status_dot.pack(side="left")
        self.status_text = ctk.CTkLabel(sidebar_status, text="未连接", font=ctk.CTkFont(size=12))
        self.status_text.pack(side="left", padx=(5, 0))
    def _build_pages_container(self):
        self.pages_frame = ctk.CTkFrame(self, corner_radius=0)
        self.pages_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.pages_frame.grid_columnconfigure(0, weight=1)
        self.pages_frame.grid_rowconfigure(0, weight=1)
        self._build_login_page()
        self._build_status_page()
        self._build_device_page()
        self._build_account_page()
        self._build_settings_page()

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)
        self.log_label = ctk.CTkLabel(self.status_bar, text="就绪", font=ctk.CTkFont(size=11))
        self.log_label.pack(side="left", padx=15)
        ctk.CTkLabel(self.status_bar, text="v2.2.0", font=ctk.CTkFont(size=11)).pack(side="right", padx=15)

    def show_page(self, page_name):
        for name, page in self.pages.items():
            page.grid_forget()
            self.nav_buttons[name].configure(fg_color="transparent")
        self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        self.nav_buttons[page_name].configure(fg_color=("gray85", "gray25"))
        if page_name == "status":
            self.after(100, self.refresh_status)
        elif page_name == "device":
            self.after(100, self.refresh_device)
        elif page_name == "account":
            self.after(100, self.refresh_account)

    def _build_login_page(self):
        page = ctk.CTkFrame(self.pages_frame, fg_color="transparent")
        self.pages["login"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="nw", pady=(0, 15))
        ctk.CTkLabel(header, text="校园网登录", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="请输入您的校园网账号信息进行登录",
                     font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).pack(anchor="w")
        card = ctk.CTkFrame(page, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        self.login_form_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.login_form_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self._build_login_form(self.login_form_frame)

    def _build_login_form(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()
        ctk.CTkLabel(parent, text="学号 / 用户名", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(parent, placeholder_text="请输入学号", height=40, font=ctk.CTkFont(size=14))
        self.username_entry.pack(fill="x", pady=(4, 12))
        if self.app_config.get("username"):
            self.username_entry.insert(0, self.app_config["username"])
        ctk.CTkLabel(parent, text="密码", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        pwd_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(4, 12))
        self.password_entry = ctk.CTkEntry(pwd_frame, placeholder_text="请输入密码", height=40, show="●", font=ctk.CTkFont(size=14))
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.pwd_show_btn = ctk.CTkButton(pwd_frame, text="👁", width=40, height=40, font=ctk.CTkFont(size=13),
                                           fg_color="transparent", command=self._toggle_pwd_visibility)
        self.pwd_show_btn.pack(side="right", padx=(6, 0))
        if self.app_config.get("save_password") and self.app_config.get("password"):
            self.password_entry.insert(0, self.app_config["password"])
        ctk.CTkLabel(parent, text="网络运营商", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.service_combo = ctk.CTkComboBox(parent, values=SERVICES, height=40, font=ctk.CTkFont(size=14))
        self.service_combo.pack(fill="x", pady=(4, 12))
        self.service_combo.set(self.app_config.get("service", "校园网"))
        opts = ctk.CTkFrame(parent, fg_color="transparent")
        opts.pack(fill="x", pady=(4, 16))
        self.save_password_var = ctk.BooleanVar(value=self.app_config.get("save_password", False))
        ctk.CTkCheckBox(opts, text="记住密码", variable=self.save_password_var, font=ctk.CTkFont(size=12)).pack(side="left")
        self.auto_login_var = ctk.BooleanVar(value=self.app_config.get("auto_login", False))
        ctk.CTkCheckBox(opts, text="自动登录", variable=self.auto_login_var, font=ctk.CTkFont(size=12)).pack(side="left", padx=(16, 0))
        self.login_btn = ctk.CTkButton(parent, text="立即登录", height=44, font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=ACCENT["primary"], hover_color=ACCENT["primary_hover"],
                                        corner_radius=10, command=self._do_login)
        self.login_btn.pack(fill="x", pady=(4, 10))
        quick = ctk.CTkFrame(parent, fg_color="transparent")
        quick.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(quick, text="查看状态", width=110, height=32, font=ctk.CTkFont(size=11),
                      fg_color="transparent", command=lambda: self.show_page("status")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(quick, text="打开设置", width=110, height=32, font=ctk.CTkFont(size=11),
                      fg_color="transparent", command=lambda: self.show_page("settings")).pack(side="left")

    def _toggle_pwd_visibility(self):
        if self.password_entry.cget("show") == "●":
            self.password_entry.configure(show="")
            self.pwd_show_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="●")
            self.pwd_show_btn.configure(text="👁")

    def _show_logged_in_view(self):
        for widget in self.login_form_frame.winfo_children():
            widget.destroy()
        info = ctk.CTkFrame(self.login_form_frame, fg_color="transparent")
        info.pack(expand=True)
        ctk.CTkLabel(info, text="已登录", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=ACCENT["success"]).pack(pady=(30, 8))
        if self.current_user:
            ctk.CTkLabel(info, text=f"用户: {self.current_user}", font=ctk.CTkFont(size=15)).pack(pady=4)
        if self.current_service:
            ctk.CTkLabel(info, text=f"运营商: {self.current_service}", font=ctk.CTkFont(size=13),
                         text_color="gray").pack(pady=4)
        ctk.CTkButton(info, text="登出", height=42, width=180, font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color=ACCENT["danger"], hover_color="#DC2626", corner_radius=10,
                      command=self._do_logout).pack(pady=(20, 8))
        ctk.CTkButton(info, text="查看状态", height=32, width=180, font=ctk.CTkFont(size=12),
                      fg_color="transparent", command=lambda: self.show_page("status")).pack(pady=4)

    def _show_login_form_view(self):
        for widget in self.login_form_frame.winfo_children():
            widget.destroy()
        self._build_login_form(self.login_form_frame)

    def _build_status_page(self):
        page = ctk.CTkFrame(self.pages_frame, fg_color="transparent")
        self.pages["status"] = page
        page.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(page, text="网络状态", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="nw", pady=(0, 4))
        ctk.CTkLabel(page, text="查看当前校园网连接状态", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).grid(row=1, column=0, sticky="nw", pady=(0, 20))
        card = ctk.CTkFrame(page, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card.grid(row=2, column=0, sticky="new", pady=(0, 15))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=20)
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        self.status_big_dot = ctk.CTkLabel(top, text="●", font=ctk.CTkFont(size=36), text_color=ACCENT["danger"])
        self.status_big_dot.pack(side="left")
        self.status_big_text = ctk.CTkLabel(top, text="未连接", font=ctk.CTkFont(size=20, weight="bold"),
                                            text_color=ACCENT["danger"])
        self.status_big_text.pack(side="left", padx=(8, 0))
        ctk.CTkButton(top, text="刷新", width=75, height=30, font=ctk.CTkFont(size=11),
                      fg_color="transparent", command=self.refresh_status).pack(side="right")
        ctk.CTkFrame(inner, height=1, fg_color="gray50").pack(fill="x", pady=15)
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        self.status_fields = {}
        fields = [("用户名", "user"), ("运营商", "service"), ("IP 地址", "ip"),
                  ("登录时间", "time"), ("接入位置", "location")]
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 2)
            f = ctk.CTkFrame(grid, fg_color="transparent")
            f.grid(row=r, column=c, sticky="nw", padx=(0, 25), pady=6)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")).pack(anchor="w")
            self.status_fields[key] = ctk.CTkLabel(f, text="—", font=ctk.CTkFont(size=14, weight="bold"))
            self.status_fields[key].pack(anchor="w", pady=(2, 0))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        self.network_hint = ctk.CTkLabel(page, text="", font=ctk.CTkFont(size=12), text_color=ACCENT["warning"])
        self.network_hint.grid(row=3, column=0, sticky="nw", pady=(10, 0))
    def _build_device_page(self):
        page = ctk.CTkFrame(self.pages_frame, fg_color="transparent")
        self.pages["device"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(page, text="在线设备", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="nw", pady=(0, 4))
        ctk.CTkLabel(page, text="当前登录设备的详细信息", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).grid(row=1, column=0, sticky="nw", pady=(0, 15))
        card = ctk.CTkFrame(page, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card.grid(row=2, column=0, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=20)
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        self.device_error_label = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=12), text_color=ACCENT["warning"])
        self.device_error_label.pack(side="left")
        ctk.CTkButton(top, text="刷新设备", width=90, height=30, font=ctk.CTkFont(size=11),
                      fg_color=ACCENT["primary"], hover_color=ACCENT["primary_hover"],
                      command=self.refresh_device).pack(side="right")
        ctk.CTkButton(top, text="下线当前设备", width=110, height=30, font=ctk.CTkFont(size=11),
                      fg_color=ACCENT["danger"], hover_color="#DC2626",
                      command=self._do_logout).pack(side="right", padx=(0, 10))
        scroll = ctk.CTkScrollableFrame(inner, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self.device_content = ctk.CTkFrame(scroll, fg_color="transparent")
        self.device_content.pack(fill="x")
        self.device_rows = []
        self._update_device_display({"提示": "请点击刷新获取设备信息"})

    def _update_device_display(self, data):
        for child in self.device_content.winfo_children():
            child.destroy()
        self.device_rows.clear()
        if not data or (isinstance(data, dict) and len(data) == 1 and "提示" in data):
            msg = data.get("提示", "暂无信息") if isinstance(data, dict) else "暂无信息"
            lbl = ctk.CTkLabel(self.device_content, text=msg, font=ctk.CTkFont(size=13), text_color=("gray40", "gray60"))
            lbl.pack(pady=30)
            self.device_rows.append(lbl)
            return
        if isinstance(data, dict):
            basic = {k: v for k, v in data.items() if k != "accountInfo" and v is not None and v != ""}
            for key, value in basic.items():
                self._add_device_row(self.device_content, key, str(value))

    def _add_device_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"), width=110).pack(side="left")
        ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=12, weight="bold"), wraplength=480).pack(side="left", padx=(12, 0))
        self.device_rows.append(row)

    def refresh_device(self):
        self.device_error_label.configure(text="")
        self._log("正在获取设备信息...")
        threading.Thread(target=self._device_worker, daemon=True).start()

    def _device_worker(self):
        try:
            client = RuijieClient()
            info = client.get_online_user_info()
            self.after(0, lambda: self._update_device_from_raw(info))
        except Exception as e:
            err = get_error_message(e)
            self.after(0, lambda: self.device_error_label.configure(text=f"获取失败: {err}"))

    def _update_device_from_raw(self, raw):
        try:
            portal = raw.get("portalOnlineUserInfo", {}) if isinstance(raw, dict) else {}
            online = raw.get("onlineUser", {}) if isinstance(raw, dict) else {}
            if not portal or portal.get("redirectUrl"):
                self._update_device_display({"提示": "当前未登录，无设备信息"})
                return
            display = {}
            # 基础信息
            display["用户名"] = portal.get("userName") or portal.get("userId", "—")
            display["IP 地址"] = portal.get("userIp", "—")
            if portal.get("userIpv6"):
                display["IPv6 地址"] = portal.get("userIpv6")
            display["MAC 地址"] = portal.get("userMac", "—")
            display["服务"] = portal.get("service", "—")
            # 接入信息（来自 onlineUser）
            if online.get("nodePhysicalLocation"):
                display["接入位置"] = online.get("nodePhysicalLocation")
            if online.get("authenticationTime"):
                display["认证时间"] = online.get("authenticationTime")
            if online.get("nodeMac"):
                display["节点 MAC"] = online.get("nodeMac")
            if online.get("isGuest") is not None:
                display["访客用户"] = "是" if online.get("isGuest") else "否"
            # 网络参数
            if portal.get("loginType"):
                lt_map = {"1": "Web 认证", "2": "客户端", "3": "微信", "4": "短信"}
                display["登录方式"] = lt_map.get(str(portal.get("loginType")), f"类型 {portal.get('loginType')}")
            if portal.get("vlanId"):
                display["VLAN ID"] = str(portal.get("vlanId"))
            if portal.get("ssid"):
                display["WiFi SSID"] = portal.get("ssid")
            if portal.get("apMac"):
                display["AP MAC"] = portal.get("apMac")
            if portal.get("portalIp") and portal.get("portalIp") != "0.0.0.0":
                display["Portal IP"] = portal.get("portalIp")
            if portal.get("welcomeTip"):
                display["欢迎语"] = portal.get("welcomeTip")
            self._update_device_display(display)
            self._log("设备信息已更新")
        except Exception as e:
            self._update_device_display({"提示": f"解析设备信息失败: {e}"})

    def _build_account_page(self):
        page = ctk.CTkFrame(self.pages_frame, fg_color="transparent")
        self.pages["account"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(page, text="账户信息", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="nw", pady=(0, 4))
        ctk.CTkLabel(page, text="查看账户详细信息和网络使用情况", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).grid(row=1, column=0, sticky="nw", pady=(0, 15))
        card = ctk.CTkFrame(page, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card.grid(row=2, column=0, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=20)
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        self.account_error_label = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=12), text_color=ACCENT["warning"])
        self.account_error_label.pack(side="left")
        ctk.CTkButton(top, text="刷新信息", width=90, height=30, font=ctk.CTkFont(size=11),
                      fg_color=ACCENT["primary"], hover_color=ACCENT["primary_hover"],
                      command=self.refresh_account).pack(side="right")
        scroll = ctk.CTkScrollableFrame(inner, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self.account_content = ctk.CTkFrame(scroll, fg_color="transparent")
        self.account_content.pack(fill="x")
        self.account_rows = []
        self._update_account_display({"提示": "请点击刷新获取账户信息"})

    def _update_account_display(self, data):
        # 清理所有子 widget（包括分隔线和标题）
        for child in self.account_content.winfo_children():
            child.destroy()
        self.account_rows.clear()
        if not data or (isinstance(data, dict) and len(data) == 1 and "提示" in data):
            msg = data.get("提示", "暂无信息") if isinstance(data, dict) else "暂无信息"
            lbl = ctk.CTkLabel(self.account_content, text=msg, font=ctk.CTkFont(size=13), text_color=("gray40", "gray60"))
            lbl.pack(pady=30)
            self.account_rows.append(lbl)
            return
        if isinstance(data, dict):
            basic = {k: v for k, v in data.items() if k != "accountInfo" and v is not None and v != ""}
            for key, value in basic.items():
                self._add_account_row(self.account_content, key, str(value))
            details = data.get("accountInfo", [])
            if details:
                sep = ctk.CTkFrame(self.account_content, height=1, fg_color="gray50")
                sep.pack(fill="x", pady=8)
                self.account_rows.append(sep)
                title_lbl = ctk.CTkLabel(self.account_content, text="详细信息", font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color=ACCENT["primary"])
                title_lbl.pack(anchor="w", pady=(0, 8))
                self.account_rows.append(title_lbl)
                for detail in details:
                    if isinstance(detail, dict):
                        t = detail.get("title", "")
                        c = detail.get("content", "")
                        if t and c:
                            self._add_account_row(self.account_content, t, c)

    def _add_account_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), text_color=("gray40", "gray60"), width=110).pack(side="left")
        ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=12, weight="bold"), wraplength=480).pack(side="left", padx=(12, 0))
        self.account_rows.append(row)

    def _build_settings_page(self):
        page = ctk.CTkFrame(self.pages_frame, fg_color="transparent")
        self.pages["settings"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(page, text="设置", font=ctk.CTkFont(size=26, weight="bold")).grid(row=0, column=0, sticky="nw", pady=(0, 4))
        ctk.CTkLabel(page, text="配置应用偏好和网络选项", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).grid(row=1, column=0, sticky="nw", pady=(0, 15))
        scroll = ctk.CTkScrollableFrame(page, fg_color="transparent")
        scroll.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        # 网络
        card2 = ctk.CTkFrame(scroll, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card2.pack(fill="x", pady=(0, 12))
        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(inner2, text="网络", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(inner2, text="HTTP 代理 (可选)", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.proxy_entry = ctk.CTkEntry(inner2, placeholder_text="例如: http://127.0.0.1:7890", height=36, font=ctk.CTkFont(size=12))
        self.proxy_entry.pack(fill="x", pady=(4, 8))
        ctk.CTkLabel(inner2, text="代理仅在网络异常时使用，正常情况下请留空", font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")).pack(anchor="w")
        # WiFi
        wifi_card = ctk.CTkFrame(scroll, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        wifi_card.pack(fill="x", pady=(0, 12))
        wifi_inner = ctk.CTkFrame(wifi_card, fg_color="transparent")
        wifi_inner.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(wifi_inner, text="WiFi 连接", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(wifi_inner, text="立即连接校园网 WiFi", width=180, height=34, font=ctk.CTkFont(size=12),
                      fg_color=ACCENT["primary"], hover_color=ACCENT["primary_hover"],
                      command=self._connect_wifi_now).pack(anchor="w", pady=(0, 0))
        ctk.CTkLabel(wifi_inner, text="手动切换到 iYanDa 校园网 WiFi", font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")).pack(anchor="w", pady=(6, 0))
        # 自动重连
        reconnect_card = ctk.CTkFrame(scroll, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        reconnect_card.pack(fill="x", pady=(0, 12))
        reconnect_inner = ctk.CTkFrame(reconnect_card, fg_color="transparent")
        reconnect_inner.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(reconnect_inner, text="自动重连", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 10))
        self.auto_reconnect_var = ctk.BooleanVar(value=self.app_config.get("auto_reconnect_enabled", False))
        self.auto_reconnect_check = ctk.CTkCheckBox(reconnect_inner, text="启用定时自动检测与重连",
                                                      variable=self.auto_reconnect_var,
                                                      command=self._on_auto_reconnect_toggle,
                                                      font=ctk.CTkFont(size=12))
        self.auto_reconnect_check.pack(anchor="w", pady=(0, 10))
        interval_frame = ctk.CTkFrame(reconnect_inner, fg_color="transparent")
        interval_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(interval_frame, text="检测间隔 (分钟)", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(side="left")
        self.interval_entry = ctk.CTkEntry(interval_frame, width=60, height=30, font=ctk.CTkFont(size=12))
        self.interval_entry.pack(side="left", padx=(10, 0))
        self.interval_entry.insert(0, str(self.app_config.get("auto_reconnect_interval", 5)))
        ctk.CTkLabel(interval_frame, text="范围: 1-60", font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")).pack(side="left", padx=(8, 0))
        acct_frame = ctk.CTkFrame(reconnect_inner, fg_color="transparent")
        acct_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(acct_frame, text="重连账户", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.reconnect_use_saved_var = ctk.BooleanVar(value=self.app_config.get("auto_reconnect_use_saved_account", True))
        ctk.CTkRadioButton(acct_frame, text="使用已保存的账号", variable=self.reconnect_use_saved_var, value=True,
                           command=self._on_reconnect_account_change, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(4, 0))
        ctk.CTkRadioButton(acct_frame, text="指定其他账号", variable=self.reconnect_use_saved_var, value=False,
                           command=self._on_reconnect_account_change, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(4, 0))
        self.reconnect_custom_frame = ctk.CTkFrame(reconnect_inner, fg_color="transparent")
        self.reconnect_custom_frame.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(self.reconnect_custom_frame, text="用户名", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.reconnect_user_entry = ctk.CTkEntry(self.reconnect_custom_frame, placeholder_text="学号/工号", height=32, font=ctk.CTkFont(size=12))
        self.reconnect_user_entry.pack(fill="x", pady=(2, 6))
        self.reconnect_user_entry.insert(0, self.app_config.get("auto_reconnect_username", ""))
        ctk.CTkLabel(self.reconnect_custom_frame, text="密码", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
        self.reconnect_pwd_entry = ctk.CTkEntry(self.reconnect_custom_frame, placeholder_text="密码", height=32, font=ctk.CTkFont(size=12), show="●")
        self.reconnect_pwd_entry.pack(fill="x", pady=(2, 6))
        self.reconnect_pwd_entry.insert(0, self.app_config.get("auto_reconnect_password", ""))
        svc_frame = ctk.CTkFrame(reconnect_inner, fg_color="transparent")
        svc_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(svc_frame, text="重连运营商", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(side="left")
        self.reconnect_service_combo = ctk.CTkComboBox(svc_frame, values=SERVICES, width=130, font=ctk.CTkFont(size=12))
        self.reconnect_service_combo.pack(side="left", padx=(10, 0))
        self.reconnect_service_combo.set(self.app_config.get("auto_reconnect_service", "校园网"))
        ctk.CTkButton(reconnect_inner, text="保存重连设置", width=140, height=34, font=ctk.CTkFont(size=12),
                      fg_color=ACCENT["primary"], hover_color=ACCENT["primary_hover"],
                      command=self._save_reconnect_settings).pack(anchor="w", pady=(10, 0))
        self._on_reconnect_account_change()
        # 数据
        card3 = ctk.CTkFrame(scroll, corner_radius=16, border_width=1, fg_color=("gray95", "gray17"), border_color=("gray80", "gray30"))
        card3.pack(fill="x", pady=(0, 12))
        inner3 = ctk.CTkFrame(card3, fg_color="transparent")
        inner3.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(inner3, text="数据", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(inner3, text="清除保存的密码", width=150, height=34, font=ctk.CTkFont(size=12),
                      fg_color="transparent", hover_color=ACCENT["danger"], command=self._clear_saved_data).pack(anchor="w")
        ctk.CTkButton(inner3, text="查看已保存账号", width=150, height=34, font=ctk.CTkFont(size=12),
                      fg_color="transparent", command=self._show_saved_account_dialog).pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(inner3, text=f"配置存储位置: {self.data_dir}", font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")).pack(anchor="w", pady=(10, 0))

    def _on_auto_reconnect_toggle(self):
        pass

    def _on_reconnect_account_change(self):
        if self.reconnect_use_saved_var.get():
            self.reconnect_custom_frame.pack_forget()
        else:
            self.reconnect_custom_frame.pack(fill="x", pady=(8, 0))

    def _save_reconnect_settings(self):
        try:
            interval = int(self.interval_entry.get().strip())
            if interval < 1:
                interval = 1
            elif interval > 60:
                interval = 60
        except ValueError:
            interval = 5
        self.app_config["auto_reconnect_enabled"] = self.auto_reconnect_var.get()
        self.app_config["auto_reconnect_interval"] = interval
        self.app_config["auto_reconnect_use_saved_account"] = self.reconnect_use_saved_var.get()
        self.app_config["auto_reconnect_username"] = self.reconnect_user_entry.get().strip()
        self.app_config["auto_reconnect_password"] = self.reconnect_pwd_entry.get().strip()
        self.app_config["auto_reconnect_service"] = self.reconnect_service_combo.get()
        self._save_config()
        self._log(f"自动重连设置已保存 (间隔: {interval} 分钟)")
        messagebox.showinfo("保存成功", f"自动重连设置已保存\n检测间隔: {interval} 分钟")
        # 重新启动定时器
        if hasattr(self, '_reconnect_timer_id') and self._reconnect_timer_id:
            self.after_cancel(self._reconnect_timer_id)
        self._schedule_reconnect()

    def _schedule_reconnect(self):
        interval_ms = self.app_config.get("auto_reconnect_interval", 5) * 60 * 1000
        self._reconnect_timer_id = self.after(interval_ms, self._scheduled_reconnect_check)

    def _scheduled_reconnect_check(self):
        try:
            if not self.app_config.get("auto_reconnect_enabled"):
                return
            # 确定使用的账号
            if self.app_config.get("auto_reconnect_use_saved_account", True):
                user = self.app_config.get("username", "")
                pwd = self.app_config.get("password", "")
            else:
                user = self.app_config.get("auto_reconnect_username", "")
                pwd = self.app_config.get("auto_reconnect_password", "")
            svc = self.app_config.get("auto_reconnect_service", "校园网")
            if not user or not pwd:
                self._log("自动重连: 未配置有效账号，跳过")
                return
            client = RuijieClient()
            status = client.get_status()
            if not status.get("online"):
                self._log(f"自动重连: 检测到未登录，正在使用 {user} 登录 {svc}...")
                threading.Thread(target=self._login_worker, args=(user, pwd, svc), daemon=True).start()
            else:
                self._log("自动重连: 已在线，无需操作")
        except Exception as e:
            self._log(f"自动重连检测失败: {e}")
        finally:
            self._schedule_reconnect()

    def _apply_mica(self):
        pass

    def _change_theme(self, choice):
        pass

    def _save_wifi_setting(self):
        pass

    def _connect_wifi_now(self):
        self._log("正在连接 iYanDa WiFi...")
        threading.Thread(target=self._wifi_worker, daemon=True).start()

    def _wifi_worker(self):
        try:
            result = WiFiManager.connect(WIFI_SSID)
            self.after(0, lambda: self._wifi_done(result))
        except Exception as e:
            self.after(0, lambda: self._wifi_done((False, str(e))))

    def _wifi_done(self, result):
        ok, msg = result
        if ok:
            self._log(f"WiFi 连接成功: {msg}")
            messagebox.showinfo("WiFi 连接", f"成功连接到 {WIFI_SSID}")
        else:
            self._log(f"WiFi 连接失败: {msg}")
            messagebox.showerror("WiFi 连接失败", msg)

    def _show_saved_account_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("已保存的账号")
        dialog.geometry("360x260")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="已保存的账号信息", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 15))
        user = self.app_config.get("username", "")
        pwd = self.app_config.get("password", "")
        saved = self.app_config.get("save_password", False)
        if not user:
            ctk.CTkLabel(frame, text="暂无保存的账号", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).pack(pady=20)
        else:
            ctk.CTkLabel(frame, text="用户名", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
            ctk.CTkLabel(frame, text=user, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(2, 12))
            ctk.CTkLabel(frame, text="密码", font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).pack(anchor="w")
            pwd_frame = ctk.CTkFrame(frame, fg_color="transparent")
            pwd_frame.pack(fill="x", pady=(2, 12))
            if saved and pwd:
                self._dialog_pwd_label = ctk.CTkLabel(pwd_frame, text="●●●●●●●●", font=ctk.CTkFont(size=14, weight="bold"))
                self._dialog_pwd_label.pack(side="left")
                def toggle():
                    if self._dialog_pwd_label.cget("text") == "●●●●●●●●":
                        self._dialog_pwd_label.configure(text=pwd)
                    else:
                        self._dialog_pwd_label.configure(text="●●●●●●●●")
                ctk.CTkButton(pwd_frame, text="👁", width=36, height=30, font=ctk.CTkFont(size=12),
                              fg_color="transparent", command=toggle).pack(side="left", padx=(8, 0))
            else:
                ctk.CTkLabel(pwd_frame, text="未保存密码", font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")).pack(anchor="w")
        ctk.CTkButton(frame, text="关闭", width=100, height=34, font=ctk.CTkFont(size=12),
                      command=dialog.destroy).pack(pady=(15, 0))
        dialog.wait_window(dialog)

    def _clear_saved_data(self):
        self.app_config["username"] = ""
        self.app_config["password"] = ""
        self.app_config["save_password"] = False
        self.app_config["auto_login"] = False
        self._save_config()
        if hasattr(self, "username_entry") and self.username_entry.winfo_exists():
            self.username_entry.delete(0, "end")
        if hasattr(self, "password_entry") and self.password_entry.winfo_exists():
            self.password_entry.delete(0, "end")
        if hasattr(self, "save_password_var"):
            self.save_password_var.set(False)
        if hasattr(self, "auto_login_var"):
            self.auto_login_var.set(False)
        self._log("已清除保存的账号数据")
        messagebox.showinfo("清除完成", "已清除保存的账号和密码数据")

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        service = self.service_combo.get()
        if not username or not password:
            messagebox.showwarning("输入错误", "请输入用户名和密码")
            return
        self.app_config["username"] = username
        self.app_config["service"] = service
        self.app_config["save_password"] = self.save_password_var.get()
        self.app_config["auto_login"] = self.auto_login_var.get()
        if self.save_password_var.get():
            self.app_config["password"] = password
        else:
            self.app_config["password"] = ""
        self._save_config()
        self.current_user = username
        self.current_service = service
        self.login_btn.configure(state="disabled", text="登录中...")
        self._log("正在登录...")
        threading.Thread(target=self._login_worker, args=(username, password, service), daemon=True).start()

    def _login_worker(self, username, password, service):
        try:
            client = RuijieClient(username=username, password=password)
            result = client.login(service_name=service)
            if result.get("success"):
                self.after(0, lambda: self._update_ui_after_login(True, result.get("message", "登录成功")))
            else:
                err = result.get("message", "登录失败")
                if "captcha" in err.lower() or "验证码" in err:
                    self.after(0, lambda: self._handle_captcha(username, password, service))
                else:
                    self.after(0, lambda: self._update_ui_after_login(False, err))
        except Exception as e:
            self.after(0, lambda: self._update_ui_after_login(False, get_error_message(e)))

    def _handle_captcha(self, username, password, service):
        self.login_btn.configure(state="normal", text="立即登录")
        dialog = CaptchaDialog(self)
        if dialog.captcha_code:
            self._log("使用验证码重新登录...")
            threading.Thread(target=self._login_worker_with_captcha,
                             args=(username, password, service, dialog.captcha_code), daemon=True).start()
        else:
            self._log("验证码输入已取消")
            self.login_btn.configure(state="normal", text="立即登录")

    def _login_worker_with_captcha(self, username, password, service, captcha):
        try:
            client = RuijieClient(username=username, password=password)
            result = client.login(service_name=service, captcha=captcha)
            self.after(0, lambda: self._update_ui_after_login(result.get("success", False),
                                                              result.get("message", "登录失败")))
        except Exception as e:
            self.after(0, lambda: self._update_ui_after_login(False, get_error_message(e)))

    def _update_ui_after_login(self, success, message):
        self.login_btn.configure(state="normal", text="立即登录")
        if success:
            self.is_logged_in = True
            self._log("登录成功")
            self.status_dot.configure(text_color=ACCENT["success"])
            self.status_text.configure(text="已连接")
            self._show_logged_in_view()
            messagebox.showinfo("登录成功", message)
        else:
            self._log(f"登录失败: {message}")
            messagebox.showerror("登录失败", message)

    def _do_logout(self):
        if not messagebox.askyesno("确认登出", "确定要登出校园网吗？"):
            return
        self._log("正在登出...")
        threading.Thread(target=self._logout_worker, daemon=True).start()

    def _logout_worker(self):
        try:
            client = RuijieClient()
            result = client.logout()
            if result.get("success"):
                self.after(0, self._logout_success)
            else:
                self.after(0, lambda: self._logout_failed(result.get("message", "登出失败")))
        except Exception as e:
            self.after(0, lambda: self._logout_failed(get_error_message(e)))

    def _logout_success(self):
        self.is_logged_in = False
        self._log("已登出")
        self.status_dot.configure(text_color=ACCENT["danger"])
        self.status_text.configure(text="未连接")
        self._show_login_form_view()
        messagebox.showinfo("登出成功", "已成功登出校园网")

    def _logout_failed(self, message):
        self._log(f"登出失败: {message}")
        messagebox.showerror("登出失败", message)

    def refresh_status(self):
        self._log("正在查询状态...")
        threading.Thread(target=self._status_worker, daemon=True).start()

    def _status_worker(self):
        try:
            client = RuijieClient()
            status = client.get_status()
            self.after(0, lambda: self._update_status_ui(status))
        except Exception as e:
            self.after(0, lambda: self._status_error(get_error_message(e)))

    def _update_status_ui(self, status):
        if status.get("online"):
            self.status_big_dot.configure(text_color=ACCENT["success"])
            self.status_big_text.configure(text="已连接", text_color=ACCENT["success"])
            self.status_dot.configure(text_color=ACCENT["success"])
            self.status_text.configure(text="已连接")
            self.network_hint.configure(text="")
        else:
            self.status_big_dot.configure(text_color=ACCENT["danger"])
            self.status_big_text.configure(text="未连接", text_color=ACCENT["danger"])
            self.status_dot.configure(text_color=ACCENT["danger"])
            self.status_text.configure(text="未连接")
            self.network_hint.configure(text="请确保已连接到燕山大学校园网 WiFi (iYanDa)")
        data = status.get("data", {})
        self.status_fields["user"].configure(text=data.get("username", "—"))
        self.status_fields["service"].configure(text=data.get("service_name", "—"))
        self.status_fields["ip"].configure(text=data.get("ip", "—"))
        self.status_fields["time"].configure(text=data.get("login_time", "—"))
        self.status_fields["location"].configure(text=data.get("location", "—"))
        self._log("状态已更新")

    def _status_error(self, message):
        self._log(f"状态查询失败: {message}")
        self.status_big_dot.configure(text_color=ACCENT["warning"])
        self.status_big_text.configure(text="查询失败", text_color=ACCENT["warning"])
        self.network_hint.configure(text="网络连接异常，请检查是否连接到校园网")

    def refresh_account(self):
        self.account_error_label.configure(text="")
        self._log("正在获取账户信息...")
        threading.Thread(target=self._account_worker, daemon=True).start()

    def _account_worker(self):
        try:
            client = RuijieClient()
            info = client.get_account_info()
            self.after(0, lambda: self._update_account_display(info))
        except Exception as e:
            err = get_error_message(e)
            self.after(0, lambda: self.account_error_label.configure(text=f"获取失败: {err}"))

    def _startup_checks(self):
        self.after(2000, self._auto_check_status)
        self.after(5000, self._schedule_reconnect)

    def _auto_check_status(self):
        self.refresh_status()
        if self.app_config.get("auto_login") and not self.is_logged_in:
            user = self.app_config.get("username", "")
            pwd = self.app_config.get("password", "")
            svc = self.app_config.get("service", "校园网")
            if user and pwd:
                self._log("自动登录中...")
                threading.Thread(target=self._login_worker, args=(user, pwd, svc), daemon=True).start()

    def _log(self, message):
        self.log_label.configure(text=message)
        print(f"[YSUNetLogin] {message}")


def main():
    ctk.set_default_color_theme("blue")
    app = YSUNetApp()
    app.mainloop()


if __name__ == "__main__":
    main()
