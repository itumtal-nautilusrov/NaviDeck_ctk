import cv2
import socket
import pickle
import struct

HOST = "0.0.0.0"
PORT = 9999

RES = [(1920, 1080), (1280, 720), (640, 480), (320, 240)]
FPS = [15, 30, 45, 60]

stats = 1 # 720p

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, RES[stats][0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RES[stats][1])
cap.set(cv2.CAP_PROP_FPS, FPS[stats])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("Waiting for laptop...")

conn, addr = server_socket.accept()
print("Connected:", addr)

while True:

    ret, frame = cap.read()
    if not ret:
        continue

    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

    data = buffer.tobytes()

    message = struct.pack("Q", len(data)) + data

    conn.sendall(message)