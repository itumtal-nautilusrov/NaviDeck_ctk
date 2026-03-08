import socket
import cv2
import pickle
import struct

JETSON_IP = "192.168.137.124"
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((JETSON_IP, PORT))

data = b""
payload_size = struct.calcsize("Q")

while True:

    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet:
            break
        data += packet

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4*1024)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    buffer = pickle.loads(frame_data)

    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    cv2.imshow("ROV Camera", frame)

    if cv2.waitKey(1) == 27:
        break