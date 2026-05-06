import tkinter as tk
import datetime
import queue
import customtkinter as ctk

from core.config import config_manager
from core.i18n import i18n_manager
from core.events import app_queue, AppEvent, AppState
from .notification import NotificationWindow
from .settings_window import SettingsWindow

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.is_hidden = False
        self.is_running = False
        self.is_standby = False
        self.remaining_time = 0

        # 统一控制相关的变量
        self.after_id = None
        self.queue_after_id = None
        self.show_colon = True
        self.tick_count = 0  # 核心引擎节拍器

        self.interval_var = ctk.StringVar(value=config_manager.get("interval"))
        self.start_time_var = ctk.StringVar(value=config_manager.get("start_time"))
        self.end_time_var = ctk.StringVar(value=config_manager.get("end_time"))

        self.COLOR_WATER = ("#1f6aa5", "#3a7ebf")
        self.COLOR_WARM_UP = ("#E5A93C", "#F2C063")
        self.COLOR_WARN = ("#C8504B", "#E5736E")
        self.COLOR_WARN_PULSE = ("#E07A76", "#F09895")
        self.COLOR_NEUTRAL = ("#888888", "#777777")

        self.setup_ui()
        self.update_ui_text()

        self.root.protocol("WM_DELETE_WINDOW", self.toggle_window)
        self.process_queue()

        self.start_reminder()

    def _(self, key: str) -> str:
        return i18n_manager.get_text(key)

    def setup_ui(self):
        width = config_manager.get_app_config("window_width")
        height = config_manager.get_app_config("window_height")

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width)
        y = (self.root.winfo_screenheight() - height) - 40
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)

        self.root.overrideredirect(True)

        import sys
        if sys.platform.startswith("win"):
            magic_color = "#000001"
            self.root.configure(fg_color=magic_color)
            self.root.wm_attributes("-transparentcolor", magic_color)

        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            border_width=1,
            border_color=("#E5E5E5", "#333333"),
            fg_color=("#FFFFFF", "#2B2B2B")
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<B1-Motion>", self.do_move)

        self.close_btn = ctk.CTkButton(
            self.main_frame,
            text="✕",
            width=30, height=30,
            corner_radius=15,
            fg_color="transparent",
            text_color="gray",
            hover_color=("#F0F0F0", "#3B3B3B"),
            command=self.toggle_window
        )
        self.close_btn.place(relx=1.0, x=-10, y=10, anchor="ne")

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=f"💧 {self._('app_name')}",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray"
        )
        self.title_label.pack(pady=(25, 5))
        self.title_label.bind("<ButtonPress-1>", self.start_move)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text=self._("status_paused"),
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 15))

        self.countdown_label = ctk.CTkLabel(
            self.main_frame,
            text="00:00",
            font=ctk.CTkFont(family="Consolas", size=65, weight="bold"),
            text_color=self.COLOR_NEUTRAL
        )
        self.countdown_label.pack(pady=(0, 0))
        self.countdown_label.bind("<ButtonPress-1>", self.start_move)

        self.rule_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=("#F5F5F5", "#333333")
        )
        self.rule_frame.pack(pady=(0, 25))
        self.rule_frame.bind("<ButtonPress-1>", self.start_move)

        self.rule_label = ctk.CTkLabel(
            self.rule_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("darkgray", "#888888")
        )
        self.rule_label.pack(padx=14, pady=4)
        self.rule_label.bind("<ButtonPress-1>", self.start_move)

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=40, pady=10)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="开启提醒",
            command=self.toggle_reminder,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(fill=tk.X, pady=(0, 10))

        self.settings_button = ctk.CTkButton(
            button_frame,
            text=f"⚙️ {self._('settings_button')}",
            command=self.open_settings,
            height=32,
            fg_color="transparent",
            hover_color=("#F0F0F0", "#3B3B3B"),
            text_color="gray",
            font=ctk.CTkFont(size=13)
        )
        self.settings_button.pack(fill=tk.X)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self._x)
        y = self.root.winfo_y() + (event.y - self._y)
        self.root.geometry(f"+{x}+{y}")

    def update_ui_text(self):
        self.title_label.configure(text=f"💧 {self._('app_name')}")
        self.settings_button.configure(text=f"⚙️ {self._('settings_button')}")

        interval = self.interval_var.get()
        start = self.start_time_var.get()
        end = self.end_time_var.get()
        self.rule_label.configure(text=f"{start} - {end} · 每 {interval} 分钟")

        self.update_countdown_label()

        if self.is_running:
            self.start_button.configure(
                text="暂停提醒",
                fg_color=("#FDEAE8", "#3B2322"),
                text_color=self.COLOR_WARN,
                hover_color=("#FADBD8", "#4A2C2B")
            )
        else:
            self.start_button.configure(
                text="开启提醒",
                fg_color=("#E5F1FB", "#1A2938"),
                text_color=self.COLOR_WATER,
                hover_color=("#D4E6F8", "#121E2A")
            )

    def process_queue(self):
        try:
            while True:
                event = app_queue.get_nowait()
                event_type = event.get("type")
                if event_type == AppEvent.TOGGLE_WINDOW:
                    self.toggle_window()
                elif event_type == "OPEN_SETTINGS":
                    self.open_settings()
                elif event_type == AppEvent.EXIT_APP:
                    self.exit_app()
        except queue.Empty:
            pass
        finally:
            self.queue_after_id = self.root.after(100, self.process_queue)

    def toggle_window(self):
        if self.is_hidden:
            self.root.deiconify()
            self.is_hidden = False
        else:
            self.root.withdraw()
            self.is_hidden = True
        AppState.is_window_hidden = self.is_hidden

    def open_settings(self):
        if self.is_hidden:
            self.toggle_window()
        settings = SettingsWindow(self.root)
        self.root.wait_window(settings.top)
        self.sync_config_to_ui()

    def sync_config_to_ui(self):
        self.interval_var.set(config_manager.get("interval"))
        self.start_time_var.set(config_manager.get("start_time"))
        self.end_time_var.set(config_manager.get("end_time"))
        self.update_ui_text()

        if self.is_running and self.is_standby:
            self.start_reminder()

    def is_in_active_range(self):
        try:
            start = datetime.datetime.strptime(self.start_time_var.get(), "%H:%M").time()
            end = datetime.datetime.strptime(self.end_time_var.get(), "%H:%M").time()
            now = datetime.datetime.now().time()
            if start < end:
                return start <= now < end
            else:
                return now >= start or now < end
        except ValueError:
            return False

    def get_seconds_to_start(self):
        try:
            now = datetime.datetime.now()
            start_time = datetime.datetime.strptime(self.start_time_var.get(), "%H:%M").time()
            target = datetime.datetime.combine(now.date(), start_time)
            if now.time() >= start_time:
                target += datetime.timedelta(days=1)
            return int((target - now).total_seconds())
        except ValueError:
            return 0

    def toggle_reminder(self):
        if self.is_running:
            self.stop_reminder()
        else:
            self.start_reminder()

    def _clear_timers(self):
        """统一清理主引擎任务"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def start_reminder(self):
        interval = self.safe_get_interval()
        if interval is None:
            NotificationWindow(self.root, self._("invalid_input"), self._("time_invalid"))
            return

        self._clear_timers()

        self.is_running = True
        self.show_colon = True
        self.tick_count = 0  # 重置节拍器

        if self.is_in_active_range():
            self.is_standby = False
            self.remaining_time = interval * 60
        else:
            self.is_standby = True
            self.remaining_time = self.get_seconds_to_start()

        self.update_ui_text()
        self.schedule_tick() # 启动统一心跳引擎

    def safe_get_interval(self):
        try:
            value = int(self.interval_var.get())
            if value <= 0: return None
            return value
        except ValueError:
            return None

    def stop_reminder(self):
        self.is_running = False
        self.is_standby = False
        self.show_colon = True

        self._clear_timers()

        self.update_ui_text()
        self.update_countdown_label()

    def schedule_tick(self):
        """核心修复：100ms 统一驱动引擎"""
        if not self.is_running: return

        self.tick_count += 1

        # 1. 严格的时间扣减：每 10 次 tick (1000ms) 走 1 秒
        if self.tick_count % 10 == 0:
            if self.remaining_time > 0:
                self.remaining_time -= 1
            else:
                self.is_running = False
                self.stop_reminder()
                NotificationWindow(self.root, self._("app_name"), self._("drink_water"), self.start_reminder)
                return

        # 2. 完美的呼吸动效：每 8 次 tick (800ms) 切换一次冒号
        if self.tick_count % 8 == 0:
            self.show_colon = not self.show_colon

        # 3. 实时同步 UI
        self.update_countdown_label()

        # 安排下一个 100ms 节拍
        self.after_id = self.root.after(100, self.schedule_tick)

    def update_countdown_label(self):
        if self.is_running:
            m, s = divmod(self.remaining_time, 60)
            h, m = divmod(m, 60)

            sep = ":" if self.show_colon else " "
            time_str = f"{h:02d}{sep}{m:02d}{sep}{s:02d}" if h > 0 else f"{m:02d}{sep}{s:02d}"

            self.countdown_label.configure(text=time_str)

            if self.is_standby:
                self.countdown_label.configure(text_color=self.COLOR_NEUTRAL)
                self.status_label.configure(text=self._("status_standby").replace("{time}", self.start_time_var.get()))
            elif self.remaining_time <= 60:
                pulse_color = self.COLOR_WARN if self.show_colon else self.COLOR_WARN_PULSE
                self.countdown_label.configure(text_color=pulse_color)
                self.status_label.configure(text=self._("status_almost"))
            elif self.remaining_time <= 300:
                self.countdown_label.configure(text_color=self.COLOR_WARM_UP)
                self.status_label.configure(text=self._("status_next_water"))
            else:
                self.countdown_label.configure(text_color=self.COLOR_WATER)
                self.status_label.configure(text=self._("status_next_water"))
        else:
            self.countdown_label.configure(text="00:00", text_color=self.COLOR_NEUTRAL)
            self.status_label.configure(text=self._("status_paused"))

    def exit_app(self):
        self._clear_timers()
        if self.queue_after_id:
            self.root.after_cancel(self.queue_after_id)
            self.queue_after_id = None
        self.root.destroy()