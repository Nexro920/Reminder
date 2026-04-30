import json
import os
from .config import config_manager, get_exe_dir
class I18nManager:
    """国际化管理：负责动态加载外部语言包"""
    def __init__(self):
        self.locales_dir = os.path.join(get_exe_dir(), "locales")
        self._translations = {}
        self.current_lang = config_manager.get("language", "zh")
        self._load_language(self.current_lang)
    def _load_language(self, lang: str):
        fallback = {
            "app_name": "Drink Water Reminder",
            "interval_label": "Reminder Interval (min):",
            "start_time_label": "Start Time (HH:MM):",
            "end_time_label": "End Time (HH:MM):",
            "countdown_label": "Time Remaining: 00:00",
        }
        file_path = os.path.join(self.locales_dir, f"{lang}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._translations = {**fallback, **data}
            except Exception as e:
                print(f"Error loading translation {lang}: {e}")
                self._translations = fallback
        else:
            self._translations = fallback
    def set_language(self, lang: str):
        """切换语言并保存到配置"""
        self.current_lang = lang
        self._load_language(lang)
        config_manager.set("language", lang)
    def get_text(self, key: str, default: str = None) -> str:
        """获取翻译文本，增加缺失时的显性占位符防御"""
        return self._translations.get(key, default if default is not None else f"[Missing: {key}]")
i18n_manager = I18nManager()

