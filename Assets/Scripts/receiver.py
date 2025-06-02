import socket
import numpy as np

# Set up the UDP server
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening for controller data...")

while True:
    data, _ = sock.recvfrom(1024)
    msg = data.decode("utf-8")
    values = list(map(float, msg.strip().split(",")))
    if len(values) != 7:
        print("Invalid data:", msg)
        continue

    pos = np.array(values[:3])
    quat = np.array(values[3:])

    print(f"Position: {pos}, Rotation (quat): {quat}")
