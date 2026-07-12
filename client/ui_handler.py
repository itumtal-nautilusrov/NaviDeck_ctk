from __future__ import annotations

import time
import socket
import os

class UIHandler:
    def __init__(self, host=None, port=None, timeout=0.05, retry_delay=1.5, logger=None):
        self.host = host or os.getenv("NAVIDECK_HOST", "127.0.0.1")
        self.port = int(port or os.getenv("NAVIDECK_COMMAND_PORT", "9997"))
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.logger = logger
        self.ui_cmd = None
        self._socket = None
        self._next_retry_at = 0.0
        self._enabled = True

    def _log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(message)

    def connect(self):
        if not self._enabled:
            return None

        if self._socket:
            return self._socket

        now = time.monotonic()
        if now < self._next_retry_at:
            return None

        try:
            sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except OSError:
            self._next_retry_at = time.monotonic() + self.retry_delay
            return None

        sock.settimeout(self.timeout)
        self._socket = sock
        self._next_retry_at = 0.0
        self._log(f"[UI] connected to {self.host}:{self.port}")
        return self._socket

    def ui_command(self, cmd):
        self.ui_cmd = cmd

        if not self._enabled:
            return self.ui_cmd

        sock = self.connect()
        if sock:
            try:
                self._log(f"[UI] tx {cmd}")
                sock.sendall((cmd + "\n").encode("utf-8"))
            except OSError:
                self.close()
                self._next_retry_at = time.monotonic() + self.retry_delay

        return self.ui_cmd

    def close(self):
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
