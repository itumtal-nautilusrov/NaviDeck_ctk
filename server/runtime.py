"""Small, swappable adapters for simulation and real ROV hardware."""

from __future__ import annotations

import json
import random
import time


class FakeTelemetrySource:
    """Safe default used when hardware is absent or unavailable."""

    def sample(self):
        electronic_temp = round(random.uniform(20.0, 39.0), 2)
        return {
            "depth": round(random.uniform(0.8, 3.6), 2),
            "velocity": round(random.uniform(0.0, 1.5), 2),
            "yaw": round(random.uniform(-180.0, 180.0), 2),
            "roll": round(random.uniform(-20.0, 20.0), 2),
            "pitch": round(random.uniform(-20.0, 20.0), 2),
            "temp_electroic": electronic_temp,
            "temp_battery": round(random.uniform(20.0, 40.0), 2),
            "battery_percent": round(random.uniform(40.0, 100.0), 2),
            "timestamp": time.time(),
            "source": "simulation",
        }


class SerialJsonTelemetrySource:
    """Reads one UTF-8 JSON telemetry object per line from a serial device.

    If the device or a valid line is unavailable, it returns simulated samples;
    UI and network clients therefore keep using the exact same schema.
    """

    def __init__(self, port, baudrate=115200, fallback=None):
        self.port = port
        self.baudrate = baudrate
        self.fallback = fallback or FakeTelemetrySource()
        self.connection = None

    def _connect(self):
        if self.connection and self.connection.is_open:
            return True
        try:
            import serial
            self.connection = serial.Serial(self.port, self.baudrate, timeout=0.2)
            print(f"[HARDWARE] telemetry serial connected: {self.port}")
            return True
        except Exception as exc:
            print(f"[HARDWARE] telemetry fallback active ({exc})")
            self.connection = None
            return False

    def sample(self):
        if not self._connect():
            return self.fallback.sample()
        try:
            line = self.connection.readline().decode("utf-8").strip()
            payload = json.loads(line)
            payload.setdefault("timestamp", time.time())
            payload.setdefault("source", "hardware")
            return payload
        except Exception:
            return self.fallback.sample()


class SerialCommandSink:
    """Forwards the unmodified newline-delimited UI protocol to hardware."""

    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.connection = None

    def __call__(self, command):
        try:
            if not self.connection or not self.connection.is_open:
                import serial
                self.connection = serial.Serial(self.port, self.baudrate, timeout=0.2)
                print(f"[HARDWARE] command serial connected: {self.port}")
            self.connection.write((command + "\n").encode("utf-8"))
        except Exception as exc:
            print(f"[HARDWARE] command not forwarded ({exc})")


def telemetry_source(mode="simulation", serial_port=None, baudrate=115200):
    if mode == "hardware" and serial_port:
        return SerialJsonTelemetrySource(serial_port, baudrate)
    return FakeTelemetrySource()
