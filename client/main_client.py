from __future__ import annotations

import json
import os
import socket
from threading import Event

try:
    from client.serial_handler import SerialHandler
except ImportError:  # pragma: no cover - script execution fallback
    from serial_handler import SerialHandler


class TelemetryClient:
    def __init__(self, host=None, port=None, timeout=5.0, on_sample=None, log=print):
        self.host = host or os.getenv("NAVIDECK_HOST", "127.0.0.1")
        self.port = int(port or os.getenv("NAVIDECK_TELEMETRY_PORT", "9998"))
        self.timeout = timeout
        self.on_sample = on_sample
        self.log = log
        self._enabled = True
        self._socket = None

    def _log(self, message):
        if self.log:
            self.log(message)

    def run(self):
        while True:
            if not self._enabled:
                Event().wait(0.2)
                continue

            try:
                with socket.create_connection((self.host, self.port), timeout=self.timeout) as conn:
                    self._socket = conn
                    conn.settimeout(0.5)
                    self._log(f"[TELEMETRY] connected to {self.host}:{self.port}")
                    buffer = ""

                    while self._enabled:
                        try:
                            chunk = conn.recv(4096)
                        except socket.timeout:
                            continue

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
                                "[TELEMETRY] depth={depth} velocity={velocity} yaw={yaw} roll={roll} pitch={pitch} temp_electroic={temp_electroic}C temp_battery={temp_battery}C battery_percent={battery_percent}%".format(
                                    depth=payload.get("depth", payload.get("pressure", 0)),
                                    velocity=payload.get("velocity", 0),
                                    yaw=payload.get("yaw", 0),
                                    roll=payload.get("roll", 0),
                                    pitch=payload.get("pitch", 0),
                                    temp_electroic=payload.get("temp_electroic", payload.get("temp_electroics", payload.get("temperature_c", 0))),
                                    temp_battery=payload.get("temp_battery", 0),
                                    battery_percent=payload.get("battery_percent", 0),
                                )
                            )
                            if self.on_sample:
                                self.on_sample(payload)

                    if not self._enabled:
                        self._log("[TELEMETRY] paused")

            except OSError as exc:
                if self._enabled:
                    self._log(f"[TELEMETRY] waiting for server: {exc}")
                    Event().wait(1)
            finally:
                self._socket = None

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
        if not self._enabled:
            self.close()

    def close(self):
        if self._socket is None:
            return

        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None


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
