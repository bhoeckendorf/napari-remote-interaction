import asyncio
from typing import Optional

from qasync import QEventLoop
from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QApplication

from .backend import ConnectionStatus, NapariBackend


class Connection(QObject):
    status_changed = Signal(object, object)
    _LOOP = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backend = None
        self._future = None

        if self._LOOP is None:
            self._LOOP = QEventLoop(QApplication.instance())
            asyncio.set_event_loop(self._LOOP)

    def start(self, hostname, port, key: str, *args, **kwargs):
        if self._future is not None:
            return
        self._backend = NapariBackend(hostname, port, key, *args, **kwargs)
        self._backend.update_status = self._update_status
        self._future = asyncio.create_task(self._backend.start())

    def stop(self):
        if self._future is None:
            return
        self._backend.stop()
        self._future.cancel()
        self._future = None
        self._backend = None

    def _update_status(self, status: ConnectionStatus, message: Optional[str] = None):
        self.status_changed.emit(status, message)
