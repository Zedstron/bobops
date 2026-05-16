from typing import Dict
from threading import Lock
from typing import Callable
from monitor_worker import LogMonitorWorker

class LogMonitorPool:
    def __init__(self):
        self.__monitors: Dict[str, LogMonitorWorker] = {}
        self.__lock = Lock()

    def start_monitor(self, name: str, path: str, callback: Callable) -> bool:
        with self.__lock:
            if name in self.__monitors and self.__monitors[name].is_alive():
                return False

            worker = LogMonitorWorker(name, path, callback)
            self.__monitors[name] = worker

            worker.start()
            return True

    def stop_monitor(self, name: str) -> bool:
        with self.__lock:
            worker = self.__monitors.get(name)
            if not worker:
                return False

            worker.stop()
            del self.__monitors[name]
            return True

    def is_running(self, name: str) -> bool:
        with self.__lock:
            worker = self.__monitors.get(name)
            return bool(worker and worker.is_alive())

    def stop_all(self):
        with self.__lock:
            names = list(self.__monitors.keys())

        for name in names:
            self.stop_monitor(name)