import socket
import threading
import sys

client_name = "*"

TARGET_HOST = "172.20.10.2"
TARGET_PORT = 9998
SENTINEL = 'QUIT<!>'

CMD_PROMPT_TXT = f"[{client_name}]>> "
MSG_PROMPT_TXT = "[CHAT WITH ALL]>> "
current_prompt = CMD_PROMPT_TXT
# MSG_PROMPT_TXT = "[CHAT WITH <NAME/IP>]>> "

TOKEN_SETNAME = "3ccaf424d754a5a65337f4b742905b1e" # setnameisneeded#0000
TOKEN_DM = "66d29e9c3fd4ff07a8046daa3fa37bcd" # directmessageisneeded#0001

# currently there is a vulnerability rn... Is that not only the server can set your name by using its token
# but the other fellow who is DM-ing with u can too :v
# they just need to type: <token>:// <your_funny_name>
# and you or even me already get cooked lol
# the reason for this is because how your message is set to travel
# from YOU -> SERVER (specifically the listen_client func) -> YA_FUNNY_FELLOW

INSTRUCTION = """========== COMMAND LINE ==========
1. Direct Message to one person := DM <CLIENT_IP>:<PORT>/<NAME>
2. Send Message to everyone := CHAT
3. Set your name := SETNAME <YOUR_NAME>
4. Back to chat := BACK<!>
5. Exit server := QUIT<!>
*Note: For 1, 2, 4 to execute, must switch to command mode [*]>> using 3: BACK<!>
=================================="""

# create TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET >> use a standard IPv4 address or hostname | socket.SOCK_STREAM >> TCP

def listen_response():
    global client
    global client_name

    try:
        while True:
            response = client.recv(1024)
            if response:
                server_msg = response.decode()
                print(35*"-")
                if TOKEN_SETNAME in server_msg and server_msg.split()[1] != TOKEN_SETNAME:
                    client_name = server_msg.split()[1]
                    print("[*] Your name is set successfully.")
                else:
                    print(f"[{TARGET_HOST}:{TARGET_PORT}]: {server_msg}")
                sys.stdout.write(current_prompt)
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

def send_msg_to_all(client, msg):
    client.send(msg)    

def set_name(client, name): # potentially a thread
    client.send(f"{TOKEN_SETNAME}//: {name}".encode("utf-8"))

def request_dm(client, fellow):
    client.send(f"")

try:
    client.connect((TARGET_HOST, TARGET_PORT))
    
    print(INSTRUCTION + "\n")
    display_prompt = CMD_PROMPT_TXT

    threading.Thread(target=listen_response).start()

    while True:
        prompt = input(display_prompt).replace('\n', '')
        if display_prompt == CMD_PROMPT_TXT:
            if prompt.upper() == "CHAT":
                display_prompt = MSG_PROMPT_TXT
                current_prompt = display_prompt
            elif "DM" in prompt.upper() and ":" in prompt.upper(): # the ":" may need to be deleted
                direct_msg()
            elif "SETNAME" in prompt.upper():
                if len(prompt.split()) == 2 and prompt.split()[0].upper() == "SETNAME":
                    set_name(client, prompt.split()[1])
                else:
                    print("[*] Invalid input. Ex: SETNAME Michael_Jackson90s")
            elif prompt.upper() == SENTINEL:
                break
            else:
                print("[*] Invalid input.")
        elif prompt.upper() == "BACK<!>" and display_prompt != CMD_PROMPT_TXT:
            display_prompt = CMD_PROMPT_TXT
            current_prompt = display_prompt
        elif display_prompt == MSG_PROMPT_TXT:
            send_msg_to_all(client, prompt.encode('utf-8'))

except ConnectionRefusedError:
    print("[*] Host is not on...")
except Exception as e:
    print("[*] An error occurs :(")
    print(e)
finally:
    client.close()
    sys.exit()

# add name => setname()