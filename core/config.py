import json
import os
import sys
def get_exe_dir() -> str:
    """获取可执行文件或脚本所在目录，兼容 PyInstaller 打包后的环境"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
class ConfigManager:
    """配置中心：统一管理用户配置与应用级常量"""
    APP_CONFIG = {
        "window_width": 400,
        "window_height": 350,
        "icon_color": (0, 128, 255),
        "icon_ellipse_color": (255, 255, 255),
        "entry_width": 10,
        "padding": 10,
        "spacing": 5,
    }
    DEFAULT_SETTINGS = {
        "language": "zh",
        "interval": "10",
        "start_time": "09:00",
        "end_time": "17:30"
    }
    def __init__(self, filename="settings.json"):
        self.config_file = os.path.join(get_exe_dir(), filename)
        self._cache = self._load()
    def _load(self) -> dict:
        """从磁盘读取配置，如果不存在或损坏则返回默认值"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_settings = json.load(f)
                    return {**self.DEFAULT_SETTINGS, **user_settings}
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.DEFAULT_SETTINGS.copy()
    def get_app_config(self, key: str, default=None):
        """获取应用级常量"""
        return self.APP_CONFIG.get(key, default)
    def get(self, key: str, default=None):
        """获取用户配置"""
        return self._cache.get(key, default)
    def set(self, key: str, value):
        """设置单条用户配置并立刻落盘"""
        self._cache[key] = value
        self.save()
    def update(self, settings: dict):
        """批量更新用户配置并落盘"""
        self._cache.update(settings)
        self.save()
    def save(self):
        """持久化保存：采用原子写入，确保文件不会因为崩溃而损坏"""
        tmp_file = self.config_file + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=4, ensure_ascii=False)
            os.replace(tmp_file, self.config_file)
        except Exception as e:
            print(f"Failed to save settings: {e}")
config_manager = ConfigManager()

