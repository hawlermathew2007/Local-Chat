import socket
import threading

# TARGET_HOST = "www.google.com"
# TARGET_PORT = 80

TARGET_HOST = "<SERVER_IP>"
TARGET_PORT = 9998
SENTINEL = 'bye brotha'

# create TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET >> use a standard IPv4 address or hostname | socket.SOCK_STREAM >> TCP

# establish a connection
client.connect((TARGET_HOST, TARGET_PORT))

def listen_response():
    pass

msg = input("[*]>> ").replace('\n', '')

while msg != SENTINEL:
    client.send(msg.encode('utf-8'))
    response = client.recv(1024)
    if response:
        print(f"[{TARGET_HOST}:{TARGET_PORT}]: {response.decode()}")
        msg = input("[*]>> ").replace('\n', '')

client.close()
