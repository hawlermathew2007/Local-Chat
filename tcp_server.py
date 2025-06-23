import socket
import threading

SENTINEL = 'bye brotha'
IP = '0.0.0.0'
PORT = 9998
FORMAT = 'utf-8'

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client, ))
        client_handler.start()
        print(f"[ACTIVE CLIENTS]: {threading.active_count() -  1}")
    
def handle_client(client_socket):
    connected = True
    client_info = client_socket.getpeername()
    client_identity = f"{client_info[0]}:{client_info[1]}"
    while connected:
        request = client_socket.recv(1024)
        if request:
            request_msg = request.decode("utf-8")
            print(f'[{client_identity}]: {request_msg}')
            if request_msg == SENTINEL:
                break
        server_msg = input(f"[*] WRITE A MSG TO {client_identity}>> ")
        client_socket.send(server_msg.encode(FORMAT))

    client_socket.close()

    # print(client_socket.getpeername())

    # with client_socket as sock:
    #     request = sock.recv(1024)
    #     print(f'[*] Received: {request.decode("utf-8")}')
    #     sock.send(b'ACK')

if __name__ == '__main__':
    main()

# use: netstat -ano|findstr <PORT>
# to check if the server is actually listening
