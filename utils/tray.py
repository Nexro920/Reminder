import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from core.events import app_queue, AppEvent, AppState
from core.i18n import i18n_manager
class TrayManager:
    """系统托盘管理器（运行在独立后台线程）"""
    def __init__(self):
        self._ = i18n_manager.get_text
        self.icon = None
    def create_image(self):
        """生成一个简单的图标 (蓝底白圆)"""
        image = Image.new('RGB', (64, 64), color=(0, 128, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
        return image
    def on_toggle(self, icon, item):
        """向主线程发送恢复/隐藏窗口事件"""
        app_queue.put({"type": AppEvent.TOGGLE_WINDOW})
    def on_open_settings(self, icon, item):
        """向主线程发送打开设置界面事件"""
        app_queue.put({"type": "OPEN_SETTINGS"})
    def on_exit(self, icon, item):
        """向主线程发送退出事件，并停止托盘自身"""
        app_queue.put({"type": AppEvent.EXIT_APP})
        self.icon.stop()
    def stop(self):
        if self.icon:
            self.icon.stop()
    def _dynamic_menu(self):
        """
        动态生成菜单：将此方法传递给 pystray.Icon，
        确保每次右键点击托盘图标时，都能实时获取最新语言的翻译文案。
        """
        def get_toggle_text(item):
            if AppState.is_window_hidden:
                return self._("hide_window")
            else:
                return self._("restore_window")
        return pystray.Menu(
            item(lambda text: self._("settings_button"), self.on_open_settings),
            item(get_toggle_text, self.on_toggle, default=True),
            item(lambda text: self._("exit_button"), self.on_exit)
        )
    def update_menu(self):
        if self.icon:
            self.icon.menu = self._dynamic_menu()
            self.icon.update_menu()
    def run(self):
        """启动系统托盘 (阻塞方法，需在独立线程运行)"""
        self.icon = pystray.Icon(
            name="DrinkWaterReminder",
            icon=self.create_image(),
            title="Drink Water Reminder",
            menu=self._dynamic_menu()
        )
        self.icon.run()
tray_manager = TrayManager()

