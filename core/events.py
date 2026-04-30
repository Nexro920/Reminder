import queue
app_queue = queue.Queue()
class AppEvent:
    TOGGLE_WINDOW = "TOGGLE_WINDOW"
    EXIT_APP = "EXIT_APP"
class AppState:
    is_window_hidden = False

