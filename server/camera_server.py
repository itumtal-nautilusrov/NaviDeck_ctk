from __future__ import annotations

import socket
import struct

import cv2
import numpy as np

RES = [(1920, 1080), (1280, 720), (640, 480), (320, 240)]
FPS = [15, 30, 45, 60]

class CameraStreamer:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port

        self.cap = cv2.VideoCapture(0)

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    def start_streaming(self, idx=2):
        target_width, target_height = RES[idx]
        target_fps = FPS[idx]

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
            self.cap.set(cv2.CAP_PROP_FPS, target_fps)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)

        print("Waiting for laptop...")

        conn, addr = server_socket.accept()
        print("Connected:", addr)

        while True:

            if self.cap.isOpened():
                ret, frame = self.cap.read()
            else:
                ret, frame = False, None

            if not ret or frame is None:
                frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "NO CAMERA DEVICE",
                    (40, target_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

            data = buffer.tobytes()

            message = struct.pack("Q", len(data)) + data
            
            conn.sendall(message)
    
    def stop_streaming(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()


def start_camera_server(idx=2, host="0.0.0.0", port=9999):
    CameraStreamer(host=host, port=port).start_streaming(idx)