import socket
import argparse
import os
from threading import Event, Thread

try:  # Supports both `python server/main_server.py` and `python -m server.main_server`.
    from .camera_server import start_camera_server
    from .telemetry_server import start_telemetry_server
    from .runtime import SerialCommandSink, telemetry_source
except ImportError:  # pragma: no cover - direct script fallback
    from camera_server import start_camera_server
    from telemetry_server import start_telemetry_server
    from runtime import SerialCommandSink, telemetry_source


def start_command_server(host="0.0.0.0", port=9997, on_command=None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    server_socket.settimeout(1.0)

    print(f"[COMMAND] listening on {host}:{port}")

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue

            print(f"[COMMAND] client connected: {addr}")
            try:
                with conn:
                    buffer = ""
                    while True:
                        try:
                            data = conn.recv(1024)
                        except ConnectionResetError:
                            print(f"[COMMAND] client reset connection: {addr}")
                            break

                        if not data:
                            break

                        print(f"[COMMAND] rx {len(data)} bytes")
                        buffer += data.decode("utf-8", errors="ignore")
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if line:
                                print(f"[COMMAND] ui cmd: {line}")
                                if on_command:
                                    on_command(line)
            except OSError as exc:
                print(f"[COMMAND] socket error from {addr}: {exc}")

            print(f"[COMMAND] client disconnected: {addr}")
    finally:
        server_socket.close()


def main():
    parser = argparse.ArgumentParser(description="NaviDeck ROV gateway")
    parser.add_argument("--mode", choices=("simulation", "hardware"), default=os.getenv("NAVIDECK_MODE", "simulation"))
    parser.add_argument("--serial-port", default=os.getenv("NAVIDECK_SERIAL_PORT"))
    parser.add_argument("--baudrate", type=int, default=int(os.getenv("NAVIDECK_BAUDRATE", "115200")))
    args = parser.parse_args()

    source = telemetry_source(args.mode, args.serial_port, args.baudrate)
    command_sink = SerialCommandSink(args.serial_port, args.baudrate) if args.mode == "hardware" and args.serial_port else None

    Thread(target=start_camera_server, args=(1,), daemon=True).start()

    Thread(target=start_command_server, kwargs={"on_command": command_sink}, daemon=True).start()

    Thread(target=start_telemetry_server, kwargs={"source": source}, daemon=True).start()

    print("========== ROV SERVER ==========")
    print("Camera Server    : 9999")
    print("Command Server   : 9997")
    print("Telemetry Server : 9998")
    print(f"Mode             : {args.mode}")
    print(f"Serial port      : {args.serial_port or 'not configured'}")
    print("===============================")

    try:
        Event().wait()
    except KeyboardInterrupt:
        print("\n[SERVER] shutting down")


if __name__ == "__main__":
    main()
