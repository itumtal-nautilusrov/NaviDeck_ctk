from __future__ import annotations

import json
import random
import socket
import threading
import time

class TelemetryStreamer:
    def __init__(self, host="0.0.0.0", port=9998, interval=0.5):
        self.host = host
        self.port = port
        self.interval = interval
        self._stop_event = threading.Event()

    def generate_sample(self):
        return {
            "pressure": round(random.uniform(0.8, 3.6), 2),
            "yaw": round(random.uniform(-180.0, 180.0), 2),
            "roll": round(random.uniform(-90.0, 90.0), 2),
            "pitch": round(random.uniform(-90.0, 90.0), 2),
            "temperature_c": round(random.uniform(8.0, 28.0), 2),
            "timestamp": time.time(),
        }

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
                        "[TELEMETRY] tx pressure={pressure} yaw={yaw} roll={roll} pitch={pitch} temp={temperature_c}C".format(
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


def start_telemetry_server(host="0.0.0.0", port=9998):
    TelemetryStreamer(host=host, port=port).start_telemetry_server()