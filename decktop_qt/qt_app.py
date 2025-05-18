import os
from pathlib import Path
import traceback
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QMessageBox, QCheckBox
)
from openvpnclient import OpenVPNClient
from websocket import create_connection
import threading
import json
import sys
import time


class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None

    def connect(self):
        self.ws = create_connection(self.url)
        return self.ws

    def receive_json(self):
        if self.ws:
            return json.loads(self.ws.recv())

    def close(self):
        if self.ws:
            self.ws.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket + VPN Client")
        self.setGeometry(200, 200, 400, 250)

        self.layout = QVBoxLayout()
        self.label = QLabel("Нажмите 'Connect' для подключения")
        self.checkbox = QCheckBox("Использовать VPN")
        self.button = QPushButton("Connect")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.connect_to_server)  # noqa

    def connect_to_server(self):
        LOCALAPPDATA = Path(os.getcwd())
        file_path = Path(LOCALAPPDATA / "client1.ovpn")
        print(file_path)
        os.environ["PATH"] += r";C:\Program Files\OpenVPN\bin"
        def task():
            vpn = None
            try:
                if self.checkbox.isChecked():
                    self.label.setText("Подключение к VPN...")
                    vpn = OpenVPNClient(str(file_path))
                    vpn.connect()
                    time.sleep(5)  # немного подождать, чтобы VPN поднялся

                    self.label.setText("VPN подключен. Подключение к WebSocket...")

                    ws_client = WebSocketClient("ws://10.8.0.1:8000/ws")
                else:
                    self.label.setText("Подключение к WebSocket...")
                    ws_client = WebSocketClient("ws://localhost:8000/ws")

                ws = ws_client.connect()
                data = ws_client.receive_json()

                self.label.setText(
                    f"✅ Успешно подключено\n"
                    f"Client IP: {data['client_ip']}\n"
                    f"Host IP: {data['host_ip']}\n"
                    f"Host Name: {data['host_name']}"
                )

                ws_client.close()

            except Exception as e:
                traceback.print_exc()
                # QMessageBox.critical(self, "Ошибка", str(e))

            finally:
                if vpn:
                    vpn.disconnect()

        threading.Thread(target=task).start()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
