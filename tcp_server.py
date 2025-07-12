import socket
import threading
import sys
import time

IP = '0.0.0.0'
PORT = 9998
FORMAT = 'utf-8'
server_name = "*"

clients = set()
clients_lock = threading.Lock()

registered_name = {} # name must be unique
ban_lists = []

TOKEN_SETNAME = "3ccaf424d754a5a65337f4b742905b1e" # setnameisneeded#0000
TOKEN_DM = "66d29e9c3fd4ff07a8046daa3fa37bcd" # directmessageisneeded#0001

CMD_PROMPT_TXT = f"[{server_name}]>> "
BOARDCAST_PROMPT_TXT = "[*] WRITE A MSG TO EVERYONE>> "
current_prompt = CMD_PROMPT_TXT

INSTRUCTION = """========== COMMAND LINE ==========
1. Direct Message to client := DM <CLIENT_IP>:<PORT>/<NAME>
2. Send Message to all clients := BC
3. Set your name := SETNAME <YOUR_NAME>
4. Check client's IP and PORT through NAME := WHOIS <NAME>
5. Switch back to command mode for command line := BACK<!>
6. Terminate server := QUIT<!>
Note:
- For 1, 2, 4 to execute, must switch to command mode [*]>> using 3: BACK<!>
- The name that you set can only see by you unfortunately...
=================================="""

# Variable for if_server_prompt_need_esc
goback_offset = 0
interruptions = [] # same as client_ids i guess # get the first element

def main(): # DM need to check if the provided client ID exist
    global current_prompt
    global CMD_PROMPT_TXT

    print(INSTRUCTION + "\n")

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, PORT))
        server.listen(5)

        print(f'[*] Listening on {IP}:{PORT}')

        threading.Thread(target=capture_client, args=(server, ), daemon=True).start() # Start capturing connection request
        threading.Thread(target=if_server_prompt_need_esc, daemon=True).start()

        time.sleep(1)

        dm_client = "" # remember to empty client
        dm_client_txt = "" # remember to empty

        while True:
            display_prompt = CMD_PROMPT_TXT
            prompt = input(display_prompt)
            if display_prompt == CMD_PROMPT_TXT:
                # actually still need to empty sth bruh
                if "DM" in prompt.upper() and ":" in prompt.upper(): # the ":" will be deleted if add name
                    is_targetted_client_exists = False
                    targetted_client_id = prompt.split()[1] # must check if len(prompt.split()) == 2
                    if len(clients) > 0:
                        if len(prompt.split()) == 2:
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
                            print("[*] Please provide one argument only. Ex: DM 192.168.0.1:53689.")
                    else:
                        print("[*] You  have no client...")
                elif prompt.upper() == "BC":
                    display_prompt = BOARDCAST_PROMPT_TXT
                    current_prompt = display_prompt
                elif "SETNAME" in prompt.upper():
                    if len(prompt.split()) == 2 and prompt.split()[0].upper() == "SETNAME":
                        set_server_name(prompt.split()[1])
                    else:
                        print("[*] Invalid input. Ex: SETNAME evil_AdMin#55")
                elif "WHOIS" in prompt.upper():
                    if len(prompt.split()) == 2 and prompt.split()[0].upper() == "WHOIS":
                        who_is(prompt.split()[1])
                    else:
                        print("[*] Invalid input. Ex: WHOIS poor_victim@LOL")
                elif prompt.upper() == "QUIT<!>":
                    break
                    # terminate all clients and threads and server
                else:
                    print("[*] Invalid input.")
            elif prompt.upper() == "BACK<!>" and display_prompt != CMD_PROMPT_TXT:
                dm_client = ""
                display_prompt = CMD_PROMPT_TXT
                current_prompt = display_prompt
            elif display_prompt == BOARDCAST_PROMPT_TXT:
                if len(clients) > 0:
                    boardcast_msg(prompt)
                else:
                    print("[*] You have no client...")
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
            client.send(msg.encode(FORMAT))


def direct_msg(client, msg):
    client.send(msg.lower().encode(FORMAT))


def delete_client():
    pass


def set_server_name(name):
    global server_name
    global CMD_PROMPT_TXT

    server_name = name
    CMD_PROMPT_TXT = f"[{server_name}]>> "
    print(f"[*] Successfully changed your name to \"{name}\"")


def set_client_name(client, name):
    # also check if the name is used
    if name not in registered_name.keys():
        client_info = client.getpeername()
        client_id = f"{client_info[0]}:{client_info[1]}"
        registered_name.update({name : client_id})
        client.send(f"{TOKEN_SETNAME}//: {name}".encode(FORMAT))
        put_in_interruptions(f"[*] {client_id} ---> {name}")
    else:
        decline_msg = "Sorry, your name has already been taken..."
        client.send(decline_msg.encode(FORMAT))


def who_is(name):
    try:
        if len(registered_name) > 0:
            client_id = registered_name[name]
            print(f"[*] {name} ---> {client_id}")
        else:
            print("[*] You have no clients...")
    except KeyError:
        print("[*] Unknown...")
    except Exception as e:
        print(f"[*] Error: {e}")


def listen_client(client_socket):
    global registered_name

    client_info = client_socket.getpeername()

    connected = True
    with clients_lock:
        clients.add(client_socket)
    try:
        while connected:
            request = client_socket.recv(1024)
            if request:
                client_id = f"{client_info[0]}:{client_info[1]}"
                if client_id in registered_name.values():
                    client_id = [registered_name for registered_name, client in registered_name.items() if client == client_id][0]
                request_msg = request.decode("utf-8")
                client_msg = f'[{client_id}]: {request_msg}'
                if TOKEN_SETNAME in request_msg and request_msg.split()[0][:-3] == TOKEN_SETNAME and request_msg.split()[1] != TOKEN_SETNAME:
                    set_client_name(client_socket, request_msg.split()[1])
                else:
                    put_in_interruptions(client_msg)

    except ConnectionResetError:
        put_in_interruptions(f"Client {client_info[0]}:{client_info[1]} disconnected...")
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

# use: netstat -ano | findstr <PORT>
# to check if the server is actually listening

# delete client + block := BAN <CLIENT> (--forerver)

# add pwn >:) => able to extract user data + send funny message box