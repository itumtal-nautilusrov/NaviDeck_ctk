import socket
from threading import Event, Thread

from camera_server import start_camera_server
from telemetry_server import start_telemetry_server


def start_command_server(host="0.0.0.0", port=9997):
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
            except OSError as exc:
                print(f"[COMMAND] socket error from {addr}: {exc}")

            print(f"[COMMAND] client disconnected: {addr}")
    finally:
        server_socket.close()


def main():

    Thread(target=start_camera_server, args=(1,), daemon=True).start()

    Thread(target=start_command_server, daemon=True).start()

    Thread(target=start_telemetry_server, daemon=True).start()

    print("========== ROV SERVER ==========")
    print("Camera Server    : 9999")
    print("Command Server   : 9997")
    print("Telemetry Server : 9998")
    print("===============================")

    try:
        Event().wait()
    except KeyboardInterrupt:
        print("\n[SERVER] shutting down")


if __name__ == "__main__":
    main()