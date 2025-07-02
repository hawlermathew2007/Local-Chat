import socket
import threading
import sys

client_name = "*"

TARGET_HOST = "<HOST_IP>"
TARGET_PORT = 9998
SENTINEL = 'QUIT<!>'

CMD_PROMPT_TXT = f"[{client_name}]>> "
MSG_PROMPT_TXT = "[CHAT WITH ALL]>> "
# MSG_PROMPT_TXT = "[CHAT WITH <NAME/IP>]>> "

INSTRUCTION = """========== COMMAND LINE ==========
1. Direct Message to one person := DM <CLIENT_IP>:<PORT>/<NAME>
2. Send Message to everyone := BC
3. Set your name := SETNAME <YOUR_NAME>
4. Back to chat := BACK<!>
5. Exit server := QUIT<!>
==================================
*Note: For 1, 2, 4 to execute, must switch to command mode [*]>> using 3: BACK<!>"""

# create TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET >> use a standard IPv4 address or hostname | socket.SOCK_STREAM >> TCP

def listen_response():
    global client

    try:
        while True:
            response = client.recv(1024)
            if response:
                print(35*"-")
                print(f"[{TARGET_HOST}:{TARGET_PORT}]: {response.decode()}")
                sys.stdout.write("[*]>> ")
                sys.stdout.flush()
    except ConnectionAbortedError:
        print("Disconnected...")
    except Exception as e:
        print("An Error occurs... Disconnected...")
        print(e)
    finally:
        client.close()
        sys.exit()

def direct_msg():
    pass

def boardcast_msg(client, msg):
    client.send(msg)    


try:
    client.connect((TARGET_HOST, TARGET_PORT))

    msg = input(CMD_PROMPT_TXT).replace('\n', '')

    threading.Thread(target=listen_response).start()

    print(INSTRUCTION)

    while msg != SENTINEL:
        boardcast_msg(client, msg.encode('utf-8'))
        msg = input(CMD_PROMPT_TXT).replace('\n', '')

except ConnectionRefusedError:
    print("[*] Host is not on...")
except Exception as e:
    print("[*] An error occurs :(")
finally:
    client.close()
    sys.exit()

# add name => setname()