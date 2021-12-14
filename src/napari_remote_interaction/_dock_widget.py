from typing import Optional

from napari_plugin_engine import napari_hook_implementation
from napari_tools_menu import register_dock_widget
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ._connection import Connection as _Connection
from .backend import ConnectionStatus


@register_dock_widget(menu="Utilities > Remote interaction")
class RemoteInteraction(QWidget):
    """
    GUI controls to enable remote interaction.
    """

    def __init__(self, napari_viewer):
        super().__init__()
        self._connection = _Connection(self)
        self._awaiting_connection = False

        self._hostname_edit = QLineEdit()
        self._port_edit = QLineEdit()
        self._key_edit = QLineEdit()
        self._status_view = QLabel("Not connected")
        self._status_style_default = self._status_view.styleSheet()

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.clicked.connect(self._on_connect)

        self._form = QFormLayout()
        self._form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self._form.addRow("Hostname", self._hostname_edit)
        self._form.addRow("Port", self._port_edit)
        self._form.addRow("Key", self._key_edit)
        self._form.addRow("Status", self._status_view)

        layout = QVBoxLayout()
        layout.addLayout(self._form)
        layout.addWidget(self._connect_btn)
        self.setLayout(layout)

        self._connection.status_changed.connect(self.on_connection_status_changed)

    def _on_connect(self):
        host = self._hostname_edit.text().strip()
        if len(host) == 0:
            QMessageBox.information(self, "Invalid configuration", "No hostname provided.")
            return

        try:
            port = int(self._port_edit.text())
        except ValueError:
            QMessageBox.information(
                self,
                "Invalid configuration",
                f'Provided port must be integer, but is "{self._port_edit.text()}".')
            return

        key = self._key_edit.text()
        if len(key) == 0:
            QMessageBox.information(
                self,
                "Invalid configuration",
                "Please provide a key.")
            return

        if self._connect_btn.text() == "Disconnect":
            self._disconnect()
        else:
            self._connect(host, port, key)

    def _connect(self, hostname, port, key, *args, **kwargs):
        self._connection.start(hostname, port, key, *args, **kwargs)

    def _disconnect(self):
        self._connection.stop()

    @Slot(object, object)
    def on_connection_status_changed(self, status: ConnectionStatus, message: Optional[str] = None):
        if status == ConnectionStatus.INACTIVE:
            for i in (self._hostname_edit, self._port_edit, self._key_edit):
                i.setEnabled(True)
            self._connect_btn.setText("Connect")
        else:
            for i in (self._hostname_edit, self._port_edit, self._key_edit):
                i.setEnabled(False)
            self._connect_btn.setText("Disconnect")

        if status == ConnectionStatus.WAITING:
            msg = "Waiting"
            color = "orange"
        elif status == ConnectionStatus.CONNECTED:
            msg = "Connected"
            color = "green"
        elif status == ConnectionStatus.ERROR:
            msg = "Error"
            color = "red"
        else:
            msg = "Inactive"
            color = None
        style = self._status_style_default if color is None else "QLabel { color : %s; }" % color
        self._status_view.setText(msg)
        self._status_view.setStyleSheet(style)

        if message is not None and len(message.strip()) > 0:
            QMessageBox.critical(self, "Error", message)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return RemoteInteraction
