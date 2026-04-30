import os
import sys

IS_WINDOWS = sys.platform.startswith('win')
if IS_WINDOWS:
    import winreg as reg

class AutoStartManager:
    """管理 Windows 开机自启"""
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "ReminderApp"

    @staticmethod
    def get_exe_path() -> str:
        return sys.executable if getattr(sys, 'frozen', False) else os.path.realpath(sys.argv[0])

    @classmethod
    def set_auto_start(cls, enabled: bool) -> bool:
        if not IS_WINDOWS:
            print("Auto-start is only supported on Windows currently.")
            return False

        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, cls.REG_PATH, 0, reg.KEY_SET_VALUE) as key:
                if enabled:
                    # 开启自启：写入当前程序的绝对路径
                    reg.SetValueEx(key, cls.APP_NAME, 0, reg.REG_SZ, cls.get_exe_path())
                else:
                    # 关闭自启：尝试删除键值
                    try:
                        reg.DeleteValue(key, cls.APP_NAME)
                    except FileNotFoundError:
                        # [修复] 如果键值本来就不存在，直接忽略，不当作错误
                        pass
            return True
        except Exception as e:
            print(f"Error setting startup: {e}")
            return False

    @classmethod
    def is_auto_start_enabled(cls) -> bool:
        if not IS_WINDOWS:
            return False

        try:
            # 以只读模式检查键值是否存在
            with reg.OpenKey(reg.HKEY_CURRENT_USER, cls.REG_PATH, 0, reg.KEY_READ) as key:
                reg.QueryValueEx(key, cls.APP_NAME)
            return True
        except OSError:
            # 找不到键值，说明没有设置开机自启
            return False