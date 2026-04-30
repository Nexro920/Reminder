import tkinter as tk
import threading
import sys
from core.config import config_manager
from core.i18n import i18n_manager
from ui.main_window import MainWindow
from utils.tray import tray_manager
import customtkinter as ctk
def main():
    root = ctk.CTk()
    app = MainWindow(root)
    tray_thread = threading.Thread(target=tray_manager.run, daemon=True, name="TrayThread")
    tray_thread.start()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        tray_manager.stop()
        if tray_thread.is_alive():
            tray_thread.join(timeout=1.0)
if __name__ == "__main__":
    main()

