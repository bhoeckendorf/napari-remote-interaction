try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

try:
    from ._dock_widget import napari_experimental_provide_dock_widget
except ModuleNotFoundError:
    pass
from .backend import RemoteInteractor
