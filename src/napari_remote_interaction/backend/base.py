from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import napari
import numpy as np

from ._serialization import _deserialize, _serialize


class ConnectionStatus(Enum):
    INACTIVE = 1
    WAITING = 2
    CONNECTED = 3
    ERROR = 4


class BaseNapariBackend(ABC):

    @abstractmethod
    async def start(self):
        return

    @abstractmethod
    def stop(self):
        return

    @abstractmethod
    def get_version(self):
        return

    def __init__(self, key: str):
        self._key = key.encode()
        self._viewer = napari.current_viewer()

    def compare_version(self, other):
        self_version = self.get_version()
        if other == self_version:
            self.update_status(ConnectionStatus.CONNECTED)
            return True
        error = f"Remote interaction version mismatch\n\nNapari backend {self_version}\nRemote interactor {other}\n\n"
        if self_version < other:
            # error += 'Please update the napari backend using the napari menu "Plugins > Install/Uninstall plugins".'
            error += 'Please update the napari backend using "pip install ' \
                     'git+https://github.com/bhoeckendorf/napari-remote-interaction.git".'
        else:
            error += 'Please update the remote interactor using "pip install ' \
                     'git+https://github.com/bhoeckendorf/napari-remote-interaction.git".'
        self.update_status(ConnectionStatus.ERROR, error)
        return ValueError(error)

    def update_status(self, status: ConnectionStatus, message: Optional[str] = None):
        """Stub; implementation is injected at runtime."""
        return

    def _get_viewer_attr(self, path):
        # path = ["layers", ("__getitem__", (0,))]

        attr = self._viewer

        try:
            if path[0] == "__backend__":
                attr = self
                path = path[1:]
        except Exception:
            pass

        for node in path:
            if isinstance(node, str):
                attr = getattr(attr, node)
            elif len(node) == 1:
                attr = getattr(attr, node[0])()
            elif len(node) > 1:
                kwargs = {} if len(node) < 3 else node[2]
                attr = getattr(attr, node[0])(*node[1], **kwargs)
            elif len(node) > 3:
                raise ValueError()
        return attr

    def call_viewer(self, message):
        try:
            retval = self._get_viewer_attr(message)
        except Exception as ex:
            retval = ex
        if retval is not None and not isinstance(retval, (bool, int, float, str, np.ndarray, Exception)):
            retval = str(type(retval))
        return retval

    def deserialize(self, x):
        try:
            return _deserialize(x, self._key)
        except RuntimeError as ex:
            self.update_status(ConnectionStatus.ERROR, str(ex))

    def serialize(self, x):
        return _serialize(x, self._key)


class BaseRemoteInteractor(ABC):

    @abstractmethod
    def get_version(self):
        return

    @abstractmethod
    def to_napari(self, x):
        return

    @abstractmethod
    def from_napari(self):
        return

    @abstractmethod
    def close(self):
        return

    def __init__(self, hostname: str, port: int, key: str):
        self.hostname = hostname
        self.port = port
        self._key = key.encode()

    def __getattr__(self, x):
        try:
            return self.__getattribute__(x)
        except AttributeError:
            return _RemoteAttr(self, [x])

    def __call__(self, x):
        if isinstance(x, _RemoteAttr):
            x = x._path
        self.to_napari(x)
        retval = self.from_napari()
        if isinstance(retval, Exception):
            raise retval
        return retval

    def set_key(self, key):
        self._key = key.encode()

    def compare_version(self):
        self(self.__backend__.compare_version(self.get_version()))

    def deserialize(self, x):
        return _deserialize(x, self._key)

    def serialize(self, x):
        return _serialize(x, self._key)


class _RemoteAttr:

    def __init__(self, remote, path=None):
        self._remote = remote
        self._path = [] if path is None else path

    def __call__(self, *args, **kwargs):
        if len(kwargs) == 0:
            self._path.append(("__call__", args))
        else:
            self._path.append(("__call__", args, kwargs))
        return self

    def __getattr__(self, x):
        self._path.append(x)
        return self

    def __len__(self):
        self._path.append(("__len__",))
        return self._remote(self)

    def __getitem__(self, x):
        self._path.append(("__getitem__", (x,)))
        return self

    def __setitem__(self, x, y):
        self._path.append(("__setitem__", (x, y)))
        return self
