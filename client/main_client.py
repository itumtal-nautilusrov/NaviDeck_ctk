from __future__ import annotations

import json
import socket
from threading import Event

try:
    from client.serial_handler import SerialHandler
except ImportError:  # pragma: no cover - script execution fallback
    from serial_handler import SerialHandler


class TelemetryClient:
    def __init__(self, host="127.0.0.1", port=9998, timeout=5.0, on_sample=None, log=print):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.on_sample = on_sample
        self.log = log

    def _log(self, message):
        if self.log:
            self.log(message)

    def run(self):
        while True:
            try:
                with socket.create_connection((self.host, self.port), timeout=self.timeout) as conn:
                    conn.settimeout(self.timeout)
                    self._log(f"[TELEMETRY] connected to {self.host}:{self.port}")
                    buffer = ""

                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            self._log("[TELEMETRY] server closed the connection")
                            break

                        self._log(f"[TELEMETRY] rx {len(chunk)} bytes")
                        buffer += chunk.decode("utf-8")
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue

                            try:
                                payload = json.loads(line)
                            except json.JSONDecodeError:
                                self._log(f"[TELEMETRY] raw {line}")
                                continue

                            self._log(
                                "[TELEMETRY] pressure={pressure} yaw={yaw} roll={roll} pitch={pitch} temp={temperature_c}C".format(
                                    **payload
                                )
                            )
                            if self.on_sample:
                                self.on_sample(payload)

            except OSError as exc:
                self._log(f"[TELEMETRY] waiting for server: {exc}")
                Event().wait(1)


def main_client():
    serial_handler = SerialHandler()
    serial_connection = serial_handler.get_serial_connection()

    print("========== ROV CLIENT ==========")
    print("Telemetry Client  : 9998")
    print("Serial Connection  : {}".format(serial_connection.port if serial_connection else "None"))
    print("===============================")

    try:
        TelemetryClient().run()
    finally:
        serial_handler.close()


if __name__ == "__main__":
    main_client()