import tkinter as tk
import sys
import customtkinter as ctk

class NotificationWindow:
    """完美融合主UI的 Toast 浮窗提醒 (含高度与按钮视觉优化)"""
    WIDTH = 340
    HEIGHT = 160  # [优化] 增加整体窗口高度，为按钮和内边距提供更多呼吸空间

    def __init__(self, parent, title: str, message: str, on_close_callback=None):
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.is_actionable = on_close_callback is not None

        self.is_closing = False
        self.callback_triggered = False

        self.top = ctk.CTkToplevel(parent)

        self.top.overrideredirect(True)
        self.top.attributes('-topmost', True)

        # 统一采用主界面的透明防撞色方案
        if sys.platform.startswith("win"):
            magic_color = "#000001"
            self.top.configure(fg_color=magic_color)
            self.top.wm_attributes("-transparentcolor", magic_color)

        self.setup_ui(title, message)
        self.position_and_animate()

        delay = 15000 if self.is_actionable else 5000
        self.auto_close_id = self.top.after(delay, self.timeout_close)

    def setup_ui(self, title, message):
        self.frame = ctk.CTkFrame(
            self.top,
            corner_radius=15,
            border_width=1,
            border_color=("#E5E5E5", "#333333"),
            fg_color=("#FFFFFF", "#2B2B2B")
        )
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        display_title = f"💧 {title}" if self.is_actionable else f"⚠️ {title}"
        title_color = ("#1f6aa5", "#3a7ebf") if self.is_actionable else ("#C8504B", "#E5736E")

        self.title_label = ctk.CTkLabel(
            self.frame,
            text=display_title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=title_color
        )
        self.title_label.pack(anchor="w", padx=20, pady=(15, 5))

        if message == "该喝水了！" or message == "Time to drink water!":
            message = "已经专注工作一段时间了，喝杯水休息一下吧。"

        self.msg_label = ctk.CTkLabel(
            self.frame,
            text=message,
            justify="left",
            wraplength=self.WIDTH - 60,
            font=ctk.CTkFont(size=13),
            text_color=("gray", "#AAAAAA")
        )
        self.msg_label.pack(anchor="w", padx=20, pady=(0, 15))

        if self.is_actionable:
            btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
            btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

            self.btn_confirm = ctk.CTkButton(
                btn_frame,
                text="喝过了",
                width=100,
                height=40,  # [优化] 增加按钮高度
                corner_radius=20, # [优化] 匹配高度的圆角
                fg_color=("#1f6aa5", "#3a7ebf"),
                hover_color=("#17568C", "#2D68A6"),
                font=ctk.CTkFont(size=14, weight="bold"), # [优化] 稍微加大字体
                command=self.confirm_action
            )
            self.btn_confirm.pack(side=tk.LEFT, expand=True, padx=(0, 5))

            self.btn_ignore = ctk.CTkButton(
                btn_frame,
                text="忽略",
                width=100,
                height=40,  # [优化] 增加按钮高度
                corner_radius=20, # [优化] 匹配高度的圆角
                fg_color="transparent",
                border_width=1,
                border_color=("#D0D0D0", "#555555"),
                text_color="gray",
                hover_color=("#F0F0F0", "#333333"),
                font=ctk.CTkFont(size=14), # [优化] 稍微加大字体
                command=self.ignore_action
            )
            self.btn_ignore.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

    def position_and_animate(self):
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()

        self.target_x = screen_width - self.WIDTH - 20
        self.target_y = screen_height - self.HEIGHT - 60

        self.current_y = screen_height
        self.top.geometry(f"{self.WIDTH}x{self.HEIGHT}+{self.target_x}+{self.current_y}")

        self.slide_in()

    def slide_in(self):
        if self.top.winfo_exists() and self.current_y > self.target_y:
            step = max(1, (self.current_y - self.target_y) // 4)
            self.current_y -= step
            self.top.geometry(f"{self.WIDTH}x{self.HEIGHT}+{self.target_x}+{self.current_y}")
            self.top.after(16, self.slide_in)

    def trigger_callback(self):
        if not self.callback_triggered and self.on_close_callback:
            self.callback_triggered = True
            self.on_close_callback()

    def timeout_close(self):
        if not self.is_closing:
            self.fade_out_and_close()

    def fade_out_and_close(self):
        self.is_closing = True
        try:
            if self.top.winfo_exists() and self.current_y < self.top.winfo_screenheight():
                step = max(1, (self.top.winfo_screenheight() - self.current_y) // 4)
                self.current_y += step
                self.top.geometry(f"{self.WIDTH}x{self.HEIGHT}+{self.target_x}+{self.current_y}")
                self.top.after(16, self.fade_out_and_close)
            else:
                self.trigger_callback()
                if self.top.winfo_exists():
                    self.top.destroy()
        except Exception:
            self.trigger_callback()

    def confirm_action(self):
        if self.is_closing: return
        if self.auto_close_id:
            self.top.after_cancel(self.auto_close_id)
        self.trigger_callback()
        self.fade_out_and_close()

    def ignore_action(self):
        if self.is_closing: return
        if self.auto_close_id:
            self.top.after_cancel(self.auto_close_id)
        self.trigger_callback()
        self.fade_out_and_close()