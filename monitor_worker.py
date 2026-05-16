import threading
from typing import Callable
from utils.monitor import monitor_log

class LogMonitorWorker:
    def __init__(self, name: str, path: str, callback: Callable):
        self.name = name
        self.path = path
        self.callback = callback

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def _run(self):
        try:
            for event in monitor_log(self.path, self.stop_event):
                if self.stop_event.is_set():
                    break

                self.callback(self.name, event)
        except Exception as e:
            self.callback(self.name, {"error": str(e)})

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=2)

    def is_alive(self):
        return self.thread.is_alive()