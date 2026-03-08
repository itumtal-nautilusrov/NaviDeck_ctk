import cv2
import socket
import pickle
import struct

HOST = "0.0.0.0"
PORT = 9999

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # 720p
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

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

    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])

    data = pickle.dumps(buffer)

    message = struct.pack("Q", len(data)) + data

    conn.sendall(message)