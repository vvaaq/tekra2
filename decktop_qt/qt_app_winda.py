import os
import subprocess
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QCheckBox
)
from websocket import create_connection
import threading
import json
import sys
import time
import shutil
import platform


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


class OpenVPNClient:
    def __init__(self, config_path):
        self.config_path = config_path
        self.process = None

    def connect(self):
        openvpn_bin = shutil.which("openvpn")
        if not openvpn_bin:
            raise FileNotFoundError("OpenVPN не найден в системном PATH.")

        print(f"Запуск OpenVPN с конфигом: {self.config_path}")

        if platform.system() == "Windows":
            self.process = subprocess.Popen(
                [openvpn_bin, "--config", str(self.config_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            self.process = subprocess.Popen(
                [openvpn_bin, "--config", str(self.config_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL
            )

        # Печатаем логи в фоне
        threading.Thread(target=self._print_logs, daemon=True).start()

    def _print_logs(self):
        for line in self.process.stdout:
            print("VPN LOG:", line.decode(errors="ignore").strip())

    def disconnect(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


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

        self.button.clicked.connect(self.connect_to_server)

        self.vpn = None

    def connect_to_server(self):
        LOCALAPPDATA = Path(os.getcwd())
        file_path = LOCALAPPDATA / "client1.ovpn"
        print(f"Используем конфиг: {file_path}")

        def task():
            try:
                if self.checkbox.isChecked():
                    self.label.setText("Подключение к VPN...")
                    self.vpn = OpenVPNClient(file_path)
                    self.vpn.connect()

                    time.sleep(1)  # Ждем поднятия VPN
                    ws_client = WebSocketClient("ws://127.0.0.1:8000/ws")
                    self.label.setText("VPN подключен. Подключение к WebSocket...")
                else:
                    ws_client = WebSocketClient("ws://127.0.0.1:8000/ws")
                    self.label.setText("Подключение к WebSocket без VPN...")

                ws_client.connect()
                data = ws_client.receive_json()

                self.label.setText(
                    f"✅ Успешно подключено\n"
                    f"Client IP: {data['client_ip']}\n"
                    f"Host IP: {data['host_ip']}\n"
                    f"Host Name: {data['host_name']}"
                )
                print(
                    f"✅ Успешно подключено\n"
                    f"Client IP: {data['client_ip']}\n"
                    f"Host IP: {data['host_ip']}\n"
                    f"Host Name: {data['host_name']}"
                )

                # ws_client.close()

            except Exception as e:
                traceback.print_exc()
                self.label.setText(f"Ошибка: {e}")

            finally:
                if self.vpn:
                    self.vpn.disconnect()

        threading.Thread(target=task).start()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
