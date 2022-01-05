import zmq
from zmq.asyncio import Context

from .base import BaseNapariBackend, BaseRemoteInteractor, ConnectionStatus
from .. import __version__


class ZmqNapariBackend(BaseNapariBackend):

    def __init__(self, hostname, port, key: str, bind_socket=False):
        super().__init__(key)
        self.context = Context.instance()
        self.socket = self.context.socket(zmq.REP)
        if bind_socket:
            self.socket.bind(f"tcp://{hostname}:{port}")
        else:
            self.socket.connect(f"tcp://{hostname}:{port}")
        self._is_active = False

    async def start(self):
        if self._is_active:
            return
        self._is_active = True
        self.update_status(ConnectionStatus.WAITING)
        try:
            while self._is_active:
                path = await self.socket.recv_serialized(self.deserialize)
                retval = self.call_viewer(path)
                await self.socket.send_serialized(retval, self.serialize)
        finally:
            self.stop()  # 2nd call after manual stop!

    def stop(self):
        self._is_active = False
        self.socket.close()
        self.context.term()
        self.update_status(ConnectionStatus.INACTIVE)

    def get_version(self):
        return __version__


class ZmqRemoteInteractor(BaseRemoteInteractor):

    def __init__(self, hostname: str, port: int, key: str, bind_socket: bool = True):
        super().__init__(hostname, port, key)
        self._context = zmq.Context.instance()
        self._socket = self._context.socket(zmq.REQ)
        if bind_socket:
            self._socket.bind(f"tcp://{hostname}:{port}")
        else:
            self._socket.connect(f"tcp://{hostname}:{port}")
        self.compare_version()  # ToDo: move to base class

    def to_napari(self, x):
        self._socket.send_serialized(x, self.serialize)

    def from_napari(self):
        return self._socket.recv_serialized(self.deserialize)

    def close(self):
        self._socket.close()
        self._context.term()

    def get_version(self):
        return __version__
