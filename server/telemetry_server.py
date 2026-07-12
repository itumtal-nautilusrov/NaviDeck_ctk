from __future__ import annotations

import json
import socket
import threading
import time

try:
    from .runtime import FakeTelemetrySource
except ImportError:  # pragma: no cover - direct script fallback
    from runtime import FakeTelemetrySource

class TelemetryStreamer:
    def __init__(self, host="0.0.0.0", port=9998, interval=0.5, source=None):
        self.host = host
        self.port = port
        self.interval = interval
        self._stop_event = threading.Event()
        self.source = source or FakeTelemetrySource()

    def generate_sample(self):
        return self.source.sample()

    def handle_client(self, conn, addr):
        print(f"[TELEMETRY] client connected: {addr}")
        with conn:
            conn.settimeout(self.interval)
            while not self._stop_event.is_set():
                payload = self.generate_sample()
                try:
                    payload_text = json.dumps(payload) + "\n"
                    conn.sendall(payload_text.encode("utf-8"))
                    print(
                        "[TELEMETRY] tx depth={depth} velocity={velocity} yaw={yaw} roll={roll} pitch={pitch} temp_electroic={temp_electroic}C temp_battery={temp_battery}C battery_percent={battery_percent}%".format(
                            **payload
                        )
                    )
                except OSError:
                    break
                time.sleep(self.interval)

        print(f"[TELEMETRY] client disconnected: {addr}")

    def start_telemetry_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.settimeout(1.0)

        print(f"[TELEMETRY] listening on {self.host}:{self.port}")

        try:
            while not self._stop_event.is_set():
                try:
                    conn, addr = server_socket.accept()
                except socket.timeout:
                    continue

                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
        finally:
            server_socket.close()

    def stop_telemetry_server(self):
        self._stop_event.set()


def start_telemetry_server(host="0.0.0.0", port=9998, source=None):
    TelemetryStreamer(host=host, port=port, source=source).start_telemetry_server()
