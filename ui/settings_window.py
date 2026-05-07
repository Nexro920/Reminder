import tkinter as tk
import datetime
import sys
import customtkinter as ctk

from core.config import config_manager
from core.i18n import i18n_manager
from .notification import NotificationWindow
from utils.tray import tray_manager
from utils.autostart import AutoStartManager

class ModernDropdown(ctk.CTkFrame):
    """自定义现代下拉框：解决原生组件无圆角、宽度不一致的硬伤"""
    def __init__(self, master, values, variable, width=200, **kwargs):
        super().__init__(master, width=width, height=32, corner_radius=8, fg_color=("#E5F1FB", "#1A2938"), cursor="hand2", **kwargs)
        self.pack_propagate(False)
        self.values = values
        self.variable = variable
        self.dropdown_window = None

        # 当前选中的文本
        self.label = ctk.CTkLabel(self, text=self.variable.get(), text_color=("#1f6aa5", "#3a7ebf"), anchor="w", font=ctk.CTkFont(size=13))
        self.label.pack(side="left", padx=15)

        # 下拉箭头
        self.arrow = ctk.CTkLabel(self, text="▼", text_color=("#1f6aa5", "#3a7ebf"), width=20)
        self.arrow.pack(side="right", padx=10)

        # 绑定点击事件到整个组件
        self.bind("<Button-1>", self.toggle_dropdown)
        self.label.bind("<Button-1>", self.toggle_dropdown)
        self.arrow.bind("<Button-1>", self.toggle_dropdown)


    def toggle_dropdown(self, event=None):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.dropdown_window.destroy()
            return

        self.dropdown_window = ctk.CTkToplevel(self.winfo_toplevel())
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.attributes('-topmost', True)

        # Windows 透明防撞色支持圆角
        if sys.platform.startswith("win"):
            magic_color = "#000001"
            self.dropdown_window.configure(fg_color=magic_color)
            self.dropdown_window.wm_attributes("-transparentcolor", magic_color)

        # 计算并严格对齐宽度和位置
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        width = self.winfo_width() - 50
        height = len(self.values) * 32 + 12

        self.dropdown_window.geometry(f"{width}x{height}+{x}+{y}")

        # 下拉悬浮卡片主体
        drop_frame = ctk.CTkFrame(
            self.dropdown_window,
            corner_radius=8,
            fg_color=("#FFFFFF", "#333333"),
            border_width=1,
            border_color=("#E5E5E5", "#444444")
        )
        drop_frame.pack(fill="both", expand=True)

        # 渲染选项列表
        for i, val in enumerate(self.values):
            btn = ctk.CTkButton(
                drop_frame, text=val,
                fg_color="transparent",
                text_color=("#1f6aa5", "#E0E0E0"),
                hover_color=("#E5F1FB", "#1A2938"),
                anchor="w",
                height=28,
                corner_radius=6,
                command=lambda v=val: self.select_value(v)
            )
            # 给上下留出呼吸空间
            pady = (6 if i == 0 else 2, 6 if i == len(self.values) - 1 else 2)
            btn.pack(fill="x", padx=6, pady=pady)

        # 失去焦点时自动关闭
        self.dropdown_window.focus_set()
        self.dropdown_window.bind("<FocusOut>", lambda e: self.after(150, self.destroy_dropdown))

    def destroy_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.dropdown_window.destroy()

    def select_value(self, value):
        self.variable.set(value)
        self.label.configure(text=value)
        self.destroy_dropdown()


class SettingsWindow:
    """设置窗口：全圆角无边框悬浮卡片 UI"""
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self._ = i18n_manager.get_text

        self.top = ctk.CTkToplevel(parent)
        self.top.resizable(False, False)
        self.top.attributes('-topmost', False)
        self.top.grab_set()

        self.top.overrideredirect(True)

        if sys.platform.startswith("win"):
            magic_color = "#000001"
            self.top.configure(fg_color=magic_color)
            self.top.wm_attributes("-transparentcolor", magic_color)

        self.padding = config_manager.get_app_config("padding")
        self.spacing = config_manager.get_app_config("spacing")

        self.interval_var = ctk.StringVar(value=config_manager.get("interval"))
        self.start_time_var = ctk.StringVar(value=config_manager.get("start_time"))
        self.end_time_var = ctk.StringVar(value=config_manager.get("end_time"))
        self.language_var = ctk.StringVar(value=config_manager.get("language"))
        self.auto_start_var = ctk.BooleanVar(value=AutoStartManager.is_auto_start_enabled())

        self._x = 0
        self._y = 0

        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(
            self.top,
            corner_radius=15,
            border_width=1,
            border_color=("#E5E5E5", "#333333"),
            fg_color=("#FFFFFF", "#2B2B2B")
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<B1-Motion>", self.do_move)

        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        title_frame.bind("<ButtonPress-1>", self.start_move)
        title_frame.bind("<B1-Motion>", self.do_move)

        title_label = ctk.CTkLabel(
            title_frame,
            text=f"⚙️ {self._('settings_title')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "#E0E0E0")
        )
        title_label.pack(side=tk.LEFT)
        title_label.bind("<ButtonPress-1>", self.start_move)

        close_btn = ctk.CTkButton(
            title_frame,
            text="✕",
            width=30, height=30,
            corner_radius=15,
            fg_color="transparent",
            text_color="gray",
            hover_color=("#F0F0F0", "#3B3B3B"),
            command=self.top.destroy
        )
        close_btn.pack(side=tk.RIGHT)

        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # --- 卡片 1: 通用设置 ---
        general_frame = ctk.CTkFrame(container, corner_radius=10, fg_color=("#F9F9F9", "#333333"))
        general_frame.pack(fill=tk.X, pady=(0, 15))

        ctk.CTkLabel(general_frame, text=self._("language_label"), font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", padx=15, pady=(15, 5))

        # [核心替换] 使用手写的现代下拉框彻底替换 CTkOptionMenu
        self.lang_menu = ModernDropdown(
            general_frame,
            values=["zh", "en"],
            variable=self.language_var,
            width=200
        )
        self.lang_menu.pack(padx=15, pady=(0, 15), anchor="w")

        self.auto_start_switch = ctk.CTkSwitch(
            general_frame,
            text=self._("set_auto_start"),
            variable=self.auto_start_var,
            font=ctk.CTkFont(size=12),
            progress_color=("#1f6aa5", "#3a7ebf")
        )
        self.auto_start_switch.pack(padx=15, pady=(0, 15), anchor="w")

        # --- 卡片 2: 提醒设置 ---
        reminder_frame = ctk.CTkFrame(container, corner_radius=10, fg_color=("#F9F9F9", "#333333"))
        reminder_frame.pack(fill=tk.X, pady=(0, 20))

        ctk.CTkLabel(reminder_frame, text=self._("interval_label"), font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", padx=15, pady=(15, 5))
        interval_entry = ctk.CTkEntry(
            reminder_frame,
            textvariable=self.interval_var,
            width=200,
            border_color=("#E0E0E0", "#444444")
        )
        interval_entry.pack(padx=15, pady=(0, 15), anchor="w")

        time_frame = ctk.CTkFrame(reminder_frame, fg_color="transparent")
        time_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        start_col = ctk.CTkFrame(time_frame, fg_color="transparent")
        start_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(start_col, text=self._("start_time_label"), font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(start_col, textvariable=self.start_time_var, border_color=("#E0E0E0", "#444444")).pack(fill="x")

        end_col = ctk.CTkFrame(time_frame, fg_color="transparent")
        end_col.pack(side="right", fill="x", expand=True)
        ctk.CTkLabel(end_col, text=self._("end_time_label"), font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(end_col, textvariable=self.end_time_var, border_color=("#E0E0E0", "#444444")).pack(fill="x")

        # --- 底部保存按钮 ---
        self.save_button = ctk.CTkButton(
            container,
            text=self._("save_button"),
            command=self.save_and_close,
            height=40,
            corner_radius=20,
            fg_color=("#1f6aa5", "#3a7ebf"),
            hover_color=("#17568C", "#2D68A6"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_button.pack(fill=tk.X)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.top.winfo_x() + (event.x - self._x)
        y = self.top.winfo_y() + (event.y - self._y)
        self.top.geometry(f"+{x}+{y}")

    def validate_inputs(self) -> str:
        try:
            interval_str = self.interval_var.get().strip()
            if not interval_str or int(interval_str) <= 0:
                return "invalid_input"

            start = datetime.datetime.strptime(self.start_time_var.get(), "%H:%M")
            end = datetime.datetime.strptime(self.end_time_var.get(), "%H:%M")

            if start == end:
                return "time_invalid"

            return ""
        except ValueError:
            return "time_invalid"

    def save_and_close(self):
        err_key = self.validate_inputs()
        if err_key:
            NotificationWindow(self.top, self._("invalid_input"), self._(err_key))
            return

        AutoStartManager.set_auto_start(self.auto_start_var.get())

        new_lang = self.language_var.get()
        config_manager.update({
            "interval": self.interval_var.get(),
            "start_time": self.start_time_var.get(),
            "end_time": self.end_time_var.get(),
            "language": new_lang
        })

        i18n_manager.set_language(new_lang)
        tray_manager.update_menu()
        self.top.destroy()

    def center_window(self):
        self.top.update_idletasks()
        width = 400
        height = self.top.winfo_reqheight() - 80
        x = (self.top.winfo_screenwidth() - width) // 2
        y = (self.top.winfo_screenheight() - height) // 2
        self.top.geometry(f"{width}x{height}+{x}+{y}")