import socket
import threading
import sys
import time

IP = '0.0.0.0'
PORT = 9998
FORMAT = 'utf-8'
SERVER_NAME = "*"

clients = set()
clients_lock = threading.Lock()

registered_name = {} # name must be unique

CMD_PROMPT_TXT = f"[{SERVER_NAME}]>> "
BOARDCAST_PROMPT_TXT = "[*] WRITE A MSG TO EVERYONE>> "

INSTRUCTION = """========== COMMAND LINE ==========
1. Direct Message to client := DM <CLIENT_IP>:<PORT>/<NAME>
2. Send Message to all clients := BC
3. Set your name := SETNAME <YOUR_NAME>
4. Check client's IP and PORT through NAME := WHOIS <NAME>
5. Switch back to command mode for command line := BACK<!>
6. Terminate server := QUIT<!>
==================================
*Note: For 1, 2, 4 to execute, must switch to command mode [*]>> using 3: BACK<!>"""

# Variable for if_server_prompt_need_esc
goback_offset = 0
interruptions = [] # same as client_ids i guess # get the first element
current_prompt = CMD_PROMPT_TXT

def main(): # DM need to check if the provided client ID exist
    global current_prompt

    print(INSTRUCTION)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, PORT))
        server.listen(5)
        print(f'[*] Listening on {IP}:{PORT}')

        threading.Thread(target=capture_client, args=(server, ), daemon=True).start() # Start capturing connection request
        threading.Thread(target=if_server_prompt_need_esc, daemon=True).start()

        time.sleep(1)

        display_prompt = CMD_PROMPT_TXT
        dm_client = "" # remember to empty client
        dm_client_txt = "" # remember to empty

        while True:
            # server can only send lowercase msg :V
            prompt = input(display_prompt).upper()
            if display_prompt == CMD_PROMPT_TXT:
                # actually still need to empty sth bruh
                if "DM" in prompt and ":" in prompt:
                    is_targetted_client_exists = False
                    targetted_client_id = prompt.split()[1]
                    if len(clients) > 0:
                        for client in clients:
                            test_client_id = f"{client.getpeername()[0]}:{client.getpeername()[1]}"
                            if test_client_id == targetted_client_id:
                                dm_client = client
                                is_targetted_client_exists = True
                        if is_targetted_client_exists:
                            dm_client_txt = f"[*] WRITE A MSG TO {targetted_client_id}>> "
                            display_prompt = dm_client_txt
                            current_prompt = display_prompt
                        else:
                            print("[*] No client with that identity...")
                    else:
                        print("[*] You currently have no client...")
                elif prompt == "BC":
                    display_prompt = BOARDCAST_PROMPT_TXT
                    current_prompt = display_prompt
                elif prompt == "QUIT<!>":
                    break
                    # terminate all clients and threads and server
                else:
                    print("[*] Invalid input.")
            elif prompt == "BACK<!>" and display_prompt != CMD_PROMPT_TXT:
                dm_client = ""
                display_prompt = CMD_PROMPT_TXT
                current_prompt = display_prompt
            elif display_prompt == BOARDCAST_PROMPT_TXT:
                if len(clients) > 0:
                    boardcast_msg(prompt)
                else:
                    print("[*] You currently have no client...")
            elif display_prompt == dm_client_txt:
                direct_msg(dm_client, prompt)

    except Exception as e:
        put_in_interruptions("An Error occurs :(")
        print(e)
        server.close()
        sys.exit()



def capture_client(server):
    while True:
        client, address = server.accept()
        put_in_interruptions(f'[*] Accepted connection from {address[0]}:{address[1]}')
        threading.Thread(target=listen_client, args=(client, )).start()
        put_in_interruptions(f"[ACTIVE CLIENTS]: {get_active_clients()}")

def boardcast_msg(msg):   
    with clients_lock:
        for client in clients:
            client.send(msg.lower().encode(FORMAT))


def direct_msg(client, msg):
    client.send(msg.lower().encode(FORMAT))

def terminate_msg():
    pass

def listen_client(client_socket):
    connected = True
    client_info = client_socket.getpeername()
    client_id = f"{client_info[0]}:{client_info[1]}"
    with clients_lock:
        clients.add(client_socket)
    try:
        while connected:
            request = client_socket.recv(1024)
            if request:
                request_msg = request.decode("utf-8")
                client_msg = f'[{client_id}]: {request_msg}'
                put_in_interruptions(client_msg)

    except ConnectionResetError:
        put_in_interruptions(f"Client {client_id} disconnected...")
    except Exception as _:
        put_in_interruptions("Server failed...")
        sys.exit()
    finally:
        with clients_lock:
            clients.remove(client_socket)
            client_socket.close()
            put_in_interruptions(f"[ACTIVE CLIENTS]: {get_active_clients()}")


def get_active_clients():
    no_server_threads = 3
    return threading.active_count() -  no_server_threads


def put_in_interruptions(interruption):
    global goback_offset
    global interruptions

    goback_offset += 1

    interruptions.append(interruption)
    # if need_print:
    #     print(interruption)


def if_server_prompt_need_esc(): # could be a thread
    global goback_offset
    global current_prompt
    global interruptions
    
    while True:
        if goback_offset > 0:
            # # with clients_lock:
            separator = 50*"-"
            if len(interruptions) > 1:
                separator = 50*"#"
            print(separator)
            for interruption in interruptions:
                print(interruption)
            sys.stdout.write(current_prompt)
            sys.stdout.flush()
            interruptions = []
            goback_offset = 0


if __name__ == '__main__':
    # capture_client() # if u just want to listen to the client
    main()

# I know yall gonna ask why no class, but stfu bruh

# use: netstat -ano|findstr <PORT>
# to check if the server is actually listening

# add name => setname() + whois()
# delete client + block := DEL <CLIENT> (--block)

# add pwn >:) => able to extract user data + send funny message