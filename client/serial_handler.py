from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Optional


def _load_serial_module():
	try:
		return import_module("serial")
	except Exception:  # pragma: no cover - optional dependency
		return None


def _load_list_ports_module():
	try:
		return import_module("serial.tools.list_ports")
	except Exception:  # pragma: no cover - optional dependency
		return None


@dataclass
class SerialConnectionInfo:
	port: str
	baudrate: int


class SerialHandler:
	def __init__(self, baudrate: int = 115200, timeout: float = 1.0, preferred_port: str | None = None):
		self.baudrate = baudrate
		self.timeout = timeout
		self.preferred_port = preferred_port
		self.connection = None

	def get_available_port(self) -> Optional[str]:
		if self.preferred_port:
			return self.preferred_port

		list_ports = _load_list_ports_module()
		if list_ports is None:
			return None

		ports = list(list_ports.comports())
		if not ports:
			return None

		return ports[0].device

	def get_serial_connection(self):
		serial = _load_serial_module()
		if serial is None:
			return None

		if self.connection and getattr(self.connection, "is_open", False):
			return self.connection

		port = self.get_available_port()
		if port is None:
			return None

		try:
			self.connection = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
		except Exception:
			self.connection = None

		return self.connection

	def close(self):
		if self.connection and getattr(self.connection, "is_open", False):
			self.connection.close()
		self.connection = None
