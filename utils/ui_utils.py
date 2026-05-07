import sys

def apply_windows_transparency(window, magic_color="#000001"):
    """为 Windows 平台应用透明防撞色，以支持无边框圆角"""
    if sys.platform.startswith("win"):
        window.configure(fg_color=magic_color)
        window.wm_attributes("-transparentcolor", magic_color)

class WindowDragger:
    """为无边框窗口提供拖拽功能的工具类"""
    def __init__(self, window, target_widgets):
        self.window = window
        self._x = 0
        self._y = 0

        # 为所有传入的组件绑定按下和拖动事件
        for widget in target_widgets:
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.window.winfo_x() + (event.x - self._x)
        y = self.window.winfo_y() + (event.y - self._y)
        self.window.geometry(f"+{x}+{y}")